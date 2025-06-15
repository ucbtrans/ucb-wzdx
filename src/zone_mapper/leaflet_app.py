from dash import Dash, html, dcc, callback, Output, Input, ALL, State, dash, ctx, callback_context
import dash_leaflet as dl
from ipyleaflet import Map, Marker, Polyline, TileLayer, Polygon
import pandas as pd
import requests
import json
import osm_mapper
from dash_resizable_panels import PanelGroup, Panel, PanelResizeHandle
import numpy as np


# Fetch the initial data
api_server = "http://23.22.241.10:8900"
#json_data = requests.get("http://128.32.234.154:8900/api/wzd/events/id").json()
json_data = requests.get(f"{api_server}/api/wzd/events/id").json()
df = pd.DataFrame(json_data)
names = list(df.ids.unique())
names.insert(0, "Demo Site")
nmaes = np.array(names)

app = Dash(__name__)

app.layout = html.Div([
    html.Div(
        [
            html.H1(children='Zone Mapping App', style={'text-align': 'center', 'width': '100%'}),
            html.Div(
                [
                    html.Button("Add Marker", id="add-marker-button", n_clicks = 0, style={'margin-right': '5px', 'padding': '10px 15px'}),
                    html.Button("Toggle Map", id="toggle-map-style", style={'margin-right': '5px', 'padding': '10px 15px'}),
                    html.Button("Save", id="save-button", style={'margin-right': '5px', 'padding': '10px 15px'}),
                    html.Button("Refine", id="refine-button", style={'margin-right': '5px', 'padding': '10px 15px'}),
                    html.Button("Place Cones", id="cone-button", style={'margin-right': '5px', 'padding': '10px 15px'}),
                    html.Button("Publish", id="publish-button", style={'margin-right': '5px', 'padding': '10px 15px'}),
                    html.Button("Undo", id="undo-button", style={'padding': '10px 15px'})
                ],
                style={'display': 'flex', 'justify-content': 'flex-end', 'gap': '5px'}
            )
        ],
        style={'display': 'flex', 'justify-content': 'space-between', "overflow-y": "scroll"}
    ),
    dcc.Dropdown(names, 'Canada', id='dropdown-selection'),
        html.Div(  # Wrap the map and JSON display in a div
        [
            PanelGroup(
                id='panel-group',
                children=[
                    Panel(
                        id='panel-1',
                        children=[
                            dl.Map(
                                id="work-zone-map",
                                style={'width': '1500px', 'height': '1000px', 'display': 'inline-block'},  # Adjust width and add display property
                                center=[37.8715, -122.2730],  # Initial center
                                zoom=5,  # Initial zoom
                                children=[
                                    dl.LayersControl([dl.BaseLayer(
                                        dl.TileLayer(id='satellite view', url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'), name='satelitte'),
                                        dl.BaseLayer(dl.TileLayer(id='tile-layer', maxZoom = 20), name='osm', checked=True)], position='topleft'),
                                    dl.Polygon(id='current-polygon', positions=[]),  # Initialize the polyline
                                    dl.LayerGroup(id='marker-group')
                                ],
                            )
                        ]
                    ),
                    PanelResizeHandle(html.Div(style={"backgroundColor": "grey", "height": "100%", "width": "5px"})),
                    Panel(
                        id='panel-2',
                        children=[
                            html.Div([
                                html.H2("GeoJSON Data", style={'text-align': 'center'}),
                                html.Div(id='json-output', style={'display': 'inline-block', 'width': '700px', 'vertical-align': 'top', 
                                        'padding': '10px', 'resize': 'horizontal', 'overflow': 'auto'}),  # Add JSON output div
                                dcc.Store(id='width-store', data=700)
                            ],
                            style={
                                    'display': 'inline-block', 
                                    'width': '700px', 
                                    'vertical-align': 'top',
                                    'border': '1px solid gray'
                                }
                            )
                        ]
                    )
                ], direction = 'horizontal'
            ),
        ],
        style={'display': 'flex'}  # Use flexbox for layout
    ),
    dcc.Store(id='coordinates-store', data={'lat': [], 'lon': []}),
    dcc.Store(id='marker-dragend-store'),
    dcc.Store(id='current-street-name'),
    html.Div(id='coordinates-display'),
    html.Div(id='video-container'), # Add a div to hold the video
    dcc.Store(id="video-url-store")
])


# Callback to create markers and reset polyline when a record is selected
@callback(
    #Output('work-zone-map', 'children'),
    Output('marker-group', 'children', allow_duplicate=True),
    Output('current-polygon', 'positions', allow_duplicate=True),
    #Output('work-zone-map', 'center'),
    Output('work-zone-map', 'zoom'),
    Output('json-output', 'children'),
    Output('current-street-name', 'data'),
    Input('dropdown-selection', 'value'),
    State('work-zone-map', 'children'),
    State('coordinates-store', 'data'),
    prevent_initial_call=True
)
def create_markers(value, current_children, stored_data):
    ctx = callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if triggered_id != 'dropdown-selection':
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update  # Return 6 no_update
    
    # Fetch new data based on the selected dropdown value
    # Demo Code
    if value == "Demo Site":
        with open("demo.json", 'r', encoding='utf-8') as f:
            geo_json_data = json.load(f)
    else:
        try:
            geo_json_data = requests.get(f"{api_server}/api/wzd/events/{value}").json()
        except Exception:
            return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
    
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
        
    # Create the layer group of all polygons
    lg = dl.LayerGroup(id='marker-group', children= markers)

    # Create the polyline connecting the markers
    polygon = dl.Polygon(id='current-polygon', positions=list(zip(lats, lons)))
    
    new_center = [sum(lats) / len(lats), sum(lons) / len(lons)]    
    new_zoom = 18
    
    street_name = geo_json_data['properties']['core-details']['properties']['properties']['core_details']['road_names']
    
    # Return the updated TileLayer, polyline, and markers
    return markers, polygon.positions, new_zoom, html.Pre(json.dumps(geo_json_data, indent=2)), street_name

@callback(
    Output('work-zone-map', 'center'),
    Input('marker-group', 'children'),
    prevent_initial_call=True
)
def update_map_center(markers):
    return markers[0]['props']['position']

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
          Output('refine-button', 'n_clicks'),
          Output('undo-button', 'n_clicks'),
          Output('current-polygon', 'positions'),
          Input('save-button', 'n_clicks'),
          Input('refine-button', 'n_clicks'),
          Input('marker-group', 'children'),
          State('dropdown-selection', 'value'),
          State('coordinates-store', 'data'),
          Input('undo-button', 'n_clicks'),
          State('current-street-name', 'data'))
def save_marker_positions(n_clicks, refine_n_clicks, markers, current_id, stored_data, undo_clicks, street_name):    
    if undo_clicks is not None:
        return {'lat': None, 'lon': None}, None, None, dash.no_update
    
    #if n_clicks is None:
    #    return dash.no_update, None, None, dash.no_update

    positions = extract_marker_positions(markers)
    print("Positions: ", positions)
    lats = [position[0] for position in positions]
    lons = [position[1] for position in positions]
    
    #if current_id[0:2] == "TM":
    #    positions = [position[::-1] for position in positions]
    #    positions = osm_mapper.buffer_linestring_geodesic(positions, 4)
    #    refine_n_clicks = None
    #    n_clicks = 1
    
    print("Street name: ", street_name)
    if refine_n_clicks != None:
        if len(positions) == 2:
            positions = [[lon, lat] for lat, lon in positions]
            positions = osm_mapper.buffer_linestring_geodesic(positions, 0.000001)
            positions = [[lon, lat] for lat, lon in positions]
        polygon = osm_mapper.create_shapely_polygon(positions)
        graph = osm_mapper.retrieve_scaled_street_graph(positions, polygon)
        street_lst = osm_mapper.get_street_list_in_graph(graph)
        street_feature = osm_mapper.get_feature(graph, street_name)
        buffer_linestring = osm_mapper.buffer_linestring_geodesic(street_feature['geometry']['coordinates'], 3.6)
        
        print("Street List", street_feature)
        print("Buffered", buffer_linestring)
        
        lons = [position[0] for position in buffer_linestring]
        lats = [position[1] for position in buffer_linestring]
        
        polygon_positions = [[lats[i], lons[i]] for i in range(len(lats))]
        
        return {**stored_data, current_id: {'lat': lats, 'lon': lons}}, None, None, None, polygon_positions
    
    if n_clicks is not None:
        lats = [position[0] for position in positions]
        lons = [position[1] for position in positions]
        polygon_positions = [[lats[i], lons[i]] for i in range(len(lats))]

        print(lats)
        print(lons)
        print(polygon_positions)

        # Store the marker positions with the current ID
        return {**stored_data, current_id: {'lat': lats, 'lon': lons}}, None, None, None, polygon_positions

    # Store the marker positions with the current ID
    return dash.no_update, None, None, None, dash.no_update

def extract_marker_positions(markers):
  positions = []
  for item in markers:
    positions.append(item['props']['position'])
  return positions


@callback(Output('coordinates-display', 'children'),
          Input('save-button', 'n_clicks'),
          Input('coordinates-store', 'data'))
def display_coordinates(n_clicks, stored_data):
    print(stored_data)
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
    Output("marker-group", 'children', allow_duplicate=True),
    Input("cone-button", 'n_clicks'),
    prevent_initial_call=True
)
def add_video_markers(clicks):
    markers = [dl.Marker(position=[37.868840,-122.254515],
                    interactive=True,
                    draggable=True,
                    id={'type': 'marker', 'index': 0}),
               dl.Marker(position=[37.868649,-122.254466],
                    interactive=True,
                    draggable=True,
                    id={'type': 'marker', 'index': 1}),
               dl.Marker(position=[37.868399,-122.254402],
                    interactive=True,
                    draggable=True,
                    id={'type': 'marker', 'index': 2}),
               dl.Marker(position=[37.869217,-122.254560],
                    interactive=True,
                    draggable=True,
                    id={'type': 'marker', 'index': 3})]
    return markers

@app.callback(
    Output("tile-layer", "className"),
    Output("tile-layer", "url"),
    Input("toggle-map-style", "n_clicks"),
    State("tile-layer", "className")
)
def toggle_map_style(n_clicks, current_state):
    if n_clicks is None:
        return 'osm', dash.no_update

    if current_state == 'osm':
        return 'satellite', dash.no_update
    else:
        return 'osm', dash.no_update
    

@app.callback(
    Output("marker-group", 'children'),
    Output("add-marker-button", "style"),
    Input("work-zone-map", "click_lat_lng"),
    Input("add-marker-button", 'n_clicks'),
    State("marker-group", 'children')
)
def add_delete_markers(clickData, n_clicks, children):
    triggered_id = ctx.triggered_id
    
    if triggered_id == "add-marker-button":
        clickData = None
    
    if (n_clicks % 2 == 1) & (clickData != None):
        new_marker = dl.Marker(position=clickData, interactive=True, draggable=True)
        children.append(new_marker)
        
    button_style = {'background-color': 'red'} if n_clicks % 2 == 1 else {'background-color': 'gray'} 
    return children, button_style

@app.callback(
    Output('width-store', 'data'),
    Input('json-output', 'style')
)
def update_width_store(style):
    return style.get('width', '700px')

app.clientside_callback(
    """
    function(message) {
        if (message && message.data && message.data.type === 'videoUrl') {
            const videoUrl = message.data.url;
            const videoElement = document.createElement('video');
            videoElement.src = videoUrl;
            videoElement.controls = true;
            videoElement.style.width = '100%';
            videoElement.style.height = 'auto';
            const container = document.getElementById('video-container');
            container.innerHTML = '';
            container.appendChild(videoElement);
        }
        return window.dash_clientside.no_update;
    }
    """,
    Output('video-container', 'children'),
    Input('video-url-store', 'data'),
    prevent_initial_call=True,
)

app.clientside_callback(
    """
    function(_, message) {
      if(message && message.data && message.data.type === 'videoUrl') {
        return message.data
      }
      return window.dash_clientside.no_update
    }
    """,
    Output("video-url-store", "data"),
    Input("video-url-store", "data"),
    State("video-url-store", "data"),
    prevent_initial_call=True,
    clientside_prop_name=["message", "event"]
)

    

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host="0.0.0.0", port=8901, debug=True, use_reloader=False)  # Set debug=True for development
