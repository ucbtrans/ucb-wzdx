from dash import Dash, html, dcc, callback, Output, Input, ALL, State
import dash_leaflet as dl
from ipyleaflet import Map, Marker, Polyline, TileLayer
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
            html.H1(children='Zone Mapping App', style={'textAlign': 'center'}),
            html.Div(
                [
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
    dl.Map(
        id="work-zone-map",
        style={'width': '1500px', 'height': '800px'},
        center=[37.8715, -122.2730],  # Initial center
        zoom=5,  # Initial zoom
        children=[
            dl.TileLayer(),
            dl.Polyline(id='current-polyline', positions=[]),  # Initialize the polyline
            []
        ]
    ),
    dcc.Store(id='coordinates-store', data={'lat': [], 'lon': []}),
    dcc.Store(id='marker-dragend-store'),
    html.Div(id='coordinates-display')
])

# Callback to create markers and reset polyline when a record is selected
@callback(
    Output('work-zone-map', 'children'),
    Input('dropdown-selection', 'value'),
    State('work-zone-map', 'children'),
    State('coordinates-store', 'data'),
    prevent_initial_call=True
)
def create_markers(value, current_children, stored_data):
    # Remove existing markers and polyline
    current_children = [
        child for child in current_children
        if not isinstance(child, (dl.Marker, dl.Polyline))
    ]
    #print(value)
    if value in stored_data:
        #print(1)
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
        polyline = dl.Polyline(id='current-polyline',
                               positions=list(zip(lats, lons)))

    else:
        # Fetch new data based on the selected dropdown value
        geo_json_data = requests.get(
            f"http://128.32.234.154:8800/api/wzd/events/{value}").json()
        coords = geo_json_data['geometry']['coordinates']
        longs = [coord[0] for coord in coords]
        lats = [coord[1] for coord in coords]

        # Remove existing markers and polyline, but keep the TileLayer
        updated_children = [child for child in current_children if isinstance(child, dl.TileLayer)]

        # Create new draggable markers
        markers = [
            dl.Marker(position=[lat, lon],
                    interactive=True,
                    draggable=True,
                    id={'type': 'marker', 'index': i})
            for i, (lat, lon) in enumerate(zip(lats, longs))
        ]

        # Create the polyline connecting the markers
        polyline = dl.Polyline(id='current-polyline', positions=list(zip(lats, longs)))

    # Return the updated TileLayer, polyline, and markers
    return [dl.TileLayer(), polyline, *markers]

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
              Input('save-button', 'n_clicks'),
              Input('work-zone-map', 'children'),
              State('dropdown-selection', 'value'),
              State('work-zone-map', 'children'),  # Get updated positions from the store
              State('coordinates-store', 'data'),
              Input('undo-button', 'n_clicks'),
              allow_duplicate=True)
def save_marker_positions(n_clicks, markers, current_id, map_children, stored_data, undo_clicks):
    if n_clicks is None:
        return dash.no_update

    if undo_clicks is not None:
        return {}

    positions = extract_marker_positions(json.dumps(markers[2:]))

    lats = [position[0] for position in positions]
    lons = [position[1] for position in positions]
    print(lats, lons)
    
    # Store the marker positions with the current ID
    return {**stored_data, current_id: {'lat': lats, 'lon': lons}}

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
    print(3)
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

if __name__ == '__main__':
    app.run_server(debug=True)
