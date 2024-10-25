import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State

from ipyleaflet import Map, Marker, Polyline, TileLayer
import ipywidgets as widgets
from dash_extensions import Ipywidget

import pandas as pd
import requests

# Fetch the initial data
json_data = requests.get("http://128.32.234.154:8800/api/wzd/events/id").json()
df = pd.DataFrame(json_data)

# Create the ipyleaflet map
m = Map(center=(37.8715, -122.2730), zoom=5)
m.add_layer(TileLayer())  # Add the default tile layer

# Create the dropdown
dropdown = widgets.Dropdown(options=df.ids.unique(), value='Canada', description='Select ID:')

# Create output widget for coordinates display
coordinates_output = widgets.HTML()

# Store to hold marker positions
marker_positions = {}

# Function to create markers and line
def create_markers(change):
    global marker_positions
    selected_id = change['new']

    if selected_id in marker_positions:
        lats = marker_positions[selected_id]['lat']
        lons = marker_positions[selected_id]['lon']
        markers = [Marker(location=(lat, lon), draggable=True) for lat, lon in zip(lats, lons)]
        line = Polyline(locations=[[lat, lon] for lat, lon in zip(lats, lons)])
    else:
        geo_json_data = requests.get(f"http://128.32.234.154:8800/api/wzd/events/{selected_id}").json()
        coords = geo_json_data['geometry']['coordinates']
        lons = [coord[0] for coord in coords]
        lats = [coord[1] for coord in coords]
        markers = [Marker(location=(lat, lon), draggable=True) for lat, lon in zip(lats, lons)]
        line = Polyline(locations=[[lat, lon] for lat, lon in zip(lats, lons)])

    # Clear existing layers and add new ones
    m.clear_layers()
    m.add_layer(TileLayer())
    for marker in markers:
        m.add_layer(marker)
        marker.on_move(handle_marker_move)
    m.add_layer(line)

# Function to handle marker move event
def handle_marker_move(**kwargs):
    global marker_positions
    for i, marker in enumerate(m.layers[1:]):  # Exclude TileLayer
        if isinstance(marker, Marker):
            if dropdown.value not in marker_positions:
                marker_positions[dropdown.value] = {'lat': [], 'lon': []}
            marker_positions[dropdown.value]['lat'][i] = kwargs['coordinates'][0]
            marker_positions[dropdown.value]['lon'][i] = kwargs['coordinates'][1]

# Initialize the markers and line
create_markers({'new': dropdown.value})

# Create the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1(children='Zone Mapping App', style={'textAlign': 'center'}),
    html.Div([
        Ipywidget(widget=dropdown),
    ]),
    html.Div([
        Ipywidget(widget=m),
    ]),
    html.Div([
        dcc.Store(id='marker-positions-store', data=marker_positions),
    ]),
    html.Div(id='coordinates-display')
])

# Callback to update coordinates display
@app.callback(
    Output('coordinates-display', 'children'),
    Input('marker-positions-store', 'data')
)
def update_coordinates_display(marker_positions):
    output = []
    for id, data in marker_positions.items():
        output.append(html.H3(f"ID: {id}"))
        output.append(html.Ul([
            html.Li(f"Latitude: {lat}, Longitude: {lon}")
            for lat, lon in zip(data['lat'], data['lon'])
        ]))
    return output

if __name__ == '__main__':
    app.run_server(debug=True)