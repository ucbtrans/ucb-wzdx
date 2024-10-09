from dash import Dash, html, dcc, callback, Output, Input, ALL, State
import dash_leaflet as dl
import pandas as pd
import requests

# Fetch the initial data
json_data = requests.get("http://128.32.234.154:8800/api/wzd/events/id").json()
df = pd.DataFrame(json_data)

app = Dash(__name__)

app.layout = html.Div([
    html.Div(
        [
            html.H1(children='Zone Mapping App',
                    style={'textAlign': 'center'}),
            html.Button("Save", id="save-button", style={'float': 'right'})
        ],
        style={'display': 'flex', 'justify-content': 'space-between'}
    ),
    dcc.Dropdown(df.ids.unique(), 'Canada', id='dropdown-selection'),
    dl.Map(
        id="work-zone-map",
        style={'width': '1500px', 'height': '800px'},
        center=[37.8715, -122.2730],  # Initial center
        zoom=5,  # Initial zoom
        children=[
            dl.TileLayer(),
            dl.Polyline(id='current-polyline', positions=[])  # Initialize the polyline
        ]
    ),
    dcc.Store(id='coordinates-store', data={'lat': [], 'lon': []}),
    dcc.Store(id='marker-dragend-store')  # Add a store for dragend events
])

# Callback to create markers and reset polyline when a record is selected
@callback(
    Output('work-zone-map', 'children'),
    Input('dropdown-selection', 'value'),
    State('work-zone-map', 'children'),
    prevent_initial_call=True
)
def create_markers(value, current_children):
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


# Callback to update the polyline positions when markers are dragged
@callback(
    Output('current-polyline', 'positions'),
    Input({'type': 'marker', 'index': ALL}, 'position')  # Track marker positions
)
def update_polyline(positions):
    # Update the polyline based on the marker positions
    if positions:
        lats = [position[0] for position in positions]
        longs = [position[1] for position in positions]
        return list(zip(lats, longs))  # Return updated positions for the polyline
    return []  # Return an empty list if no positions are available



@callback(Output('coordinates-store', 'data'),
              Input('save-button', 'n_clicks'),
              State({'type': 'marker', 'index': ALL}, 'position'))
def save_marker_positions(n_clicks, positions):
    if n_clicks is None:
        return dash.no_update  # Don't update if the button hasn't been clicked

    lats = [position[0] for position in positions]
    lons = [position[1] for position in positions]
    return {'lat': lats, 'lon': lons}  # Save the marker positions to the store

if __name__ == '__main__':
    app.run_server(debug=True)
