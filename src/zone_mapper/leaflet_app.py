from dash import Dash, html, dcc, callback, Output, Input, ALL, State, dash
import dash_leaflet as dl
from ipyleaflet import Map, Marker, Polyline, TileLayer, Polygon
import pandas as pd
import requests
import json

# Fetch the initial data
json_data = requests.get("http://128.32.234.154:8800/api/wzd/events/id").json()
df = pd.DataFrame(json_data)

app = Dash(__name__)

app.layout = html.Div([
    html.Div(
        [
            html.H1(children='Zone Mapping App', style={'text-align': 'center'}),
            html.Div(
                [
                    html.Button("Toggle Map", id="toggle-map-style", style={'margin-right': '5px', 'padding': '10px 15px'}),
                    html.Button("Save", id="save-button", style={'margin-right': '5px', 'padding': '10px 15px'}),
                    html.Button("Publish", id="publish-button", style={'margin-right': '5px', 'padding': '10px 15px'}),
                    html.Button("Undo", id="undo-button", style={'padding': '10px 15px'})
                ],
                style={'float': 'right'}
            )
        ],
        style={'display': 'flex', 'justify-content': 'space-between', "overflow-y": "scroll"}
    ),
    dcc.Dropdown(df.ids.unique(), 'Canada', id='dropdown-selection'),
        html.Div(  # Wrap the map and JSON display in a div
        [
            dl.Map(
                id="work-zone-map",
                style={'width': '1500px', 'height': '800px', 'display': 'inline-block'},  # Adjust width and add display property
                center=[37.8715, -122.2730],  # Initial center
                zoom=5,  # Initial zoom
                children=[
                    dl.TileLayer(id='tile-layer', className = 'osm'),
                    dl.Polygon(id='current-polygon', positions=[]),  # Initialize the polyline
                    []
                ]
            ),
            html.Div([
                html.H2("GeoJSON Data", style={'text-align': 'center'}),
                html.Div(id='json-output', style={'display': 'inline-block', 'width': '700px', 'vertical-align': 'top', 
                        'padding': '10px'}),  # Add JSON output div
            ],
            style={
                    'display': 'inline-block', 
                    'width': '700px', 
                    'vertical-align': 'top',
                    'border': '1px solid gray'
                }
            )

        ],
        style={'display': 'flex'}  # Use flexbox for layout
    ),
    dcc.Store(id='coordinates-store', data={'lat': [], 'lon': []}),
    dcc.Store(id='marker-dragend-store'),
    html.Div(id='coordinates-display')
])

# Callback to create markers and reset polyline when a record is selected
@callback(
    Output('work-zone-map', 'children'),
    Output('work-zone-map', 'center'),
    Output('work-zone-map', 'zoom'),
    Output('json-output', 'children'),
    Input('dropdown-selection', 'value'),
    State('work-zone-map', 'children'),
    State('coordinates-store', 'data'),
    prevent_initial_call=True
)
def create_markers(value, current_children, stored_data):
    # Fetch new data based on the selected dropdown value
    geo_json_data = requests.get(f"http://128.32.234.154:8800/api/wzd/events/{value}").json()
    
    
    # Remove existing markers and polyline
    current_children = [
        child for child in current_children
        if not isinstance(child, (dl.Marker, dl.Polygon))
    ]

    if value in stored_data:
        # Use stored data to create markers
        lats = stored_data[value]['lat']
        lons = stored_data[value]['lon']
        markers = [
            dl.Marker(position=[lat, lon],
                      interactive=True,
                      draggable=True,
                      id={'type': 'marker', 'index': i})
            for i, (lat, lon) in enumerate(zip(lats, lons))
        ]


    else:
        coords = geo_json_data['geometry']['coordinates']
        lons = [coord[0] for coord in coords]
        lats = [coord[1] for coord in coords]

        # Remove existing markers and polyline, but keep the TileLayer
        updated_children = [child for child in current_children if isinstance(child, dl.TileLayer)]

        # Create new draggable markers
        markers = [
            dl.Marker(position=[lat, lon],
                    interactive=True,
                    draggable=True,
                    id={'type': 'marker', 'index': i})
            for i, (lat, lon) in enumerate(zip(lats, lons))
        ]

    # Create the polyline connecting the markers
    polygon = dl.Polygon(id='current-polygon', positions=list(zip(lats, lons)))
    
    new_center = [lats[0], lons[0]]
    new_zoom = 18

    # Return the updated TileLayer, polyline, and markers
    return [dl.TileLayer(), polygon, *markers], new_center, new_zoom, html.Pre(json.dumps(geo_json_data, indent=2))

@callback(
    Output('marker-dragend-store', 'data'),
    Input({'type': 'marker', 'index': ALL}, 'dragend'),  # Use dragend event
    State('marker-dragend-store', 'data'),
    prevent_initial_call=True
)
def update_marker_positions(dragend_events, current_data):
    if current_data is None:
        current_data = {}  # Initialize if it's the first dragend event

    for i, dragend_event in enumerate(dragend_events):
        if dragend_event:
            new_position = dragend_event['lat_lng']  # Get new position from event data
            current_data[i] = new_position

    return current_data


@callback(Output('coordinates-store', 'data'),
          Output('save-button', 'n_clicks'),
          Output('undo-button', 'n_clicks'),
          Output('current-polygon', 'positions'),
          Input('save-button', 'n_clicks'),
          Input('work-zone-map', 'children'),
          State('dropdown-selection', 'value'),
          State('coordinates-store', 'data'),
          Input('undo-button', 'n_clicks'),
          allow_duplicate=True)
def save_marker_positions(n_clicks, markers, current_id, stored_data, undo_clicks):    
    if undo_clicks is not None:
        return {'lat': None, 'lon': None}, None, None, dash.no_update
    
    if n_clicks is None:
        return dash.no_update, None, None, dash.no_update

    positions = extract_marker_positions(json.dumps(markers[2:]))

    lats = [position[0] for position in positions]
    lons = [position[1] for position in positions]
    print(lats, lons)
    
    polygon_positions = [[lats[i], lons[i]] for i in range(len(lats))]

    
    # Store the marker positions with the current ID
    return {**stored_data, current_id: {'lat': lats, 'lon': lons}}, None, None, polygon_positions

def extract_marker_positions(json_data):
  data = json.loads(json_data)
  positions = []
  for item in data:
    if item['type'] == 'Marker':
      positions.append(tuple(item['props']['position']))
  return positions



@callback(Output('coordinates-display', 'children'),
          Input('save-button', 'n_clicks'),
          Input('coordinates-store', 'data'))
def display_coordinates(n_clicks, stored_data):
    if not stored_data:
        return "No coordinates"

    output = []
    stored_data.pop('lat')
    stored_data.pop('lon')
    
    for id, data in stored_data.items():
        print(id)
        print(data)
        output.append(html.H3(f"ID: {id}"))
        output.append(html.Ul([
            html.Li(f"Latitude: {lat}, Longitude: {lon}")
            for lat, lon in zip(data['lat'], data['lon'])
        ]))

    return output

@app.callback(
    Output("tile-layer", "className"),
    Output("tile-layer", "url"),
    Input("toggle-map-style", "n_clicks"),
    State("tile-layer", "className")
)
def toggle_map_style(n_clicks, current_state):
    if n_clicks is None:
        return 'osm', None

    if current_state == 'osm':
        return 'satellite', "http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
    else:
        return 'osm', None
    
#
#@app.callback(
#    Output(""),
#    Input("work-zone-map", "clickData")
#)
#def add_delete_markers(clickData):
#    latlong = clickData.latlong
    

if __name__ == '__main__':
    app.run_server(debug=True)
