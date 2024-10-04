from dash import Dash, html, dcc, callback, Output, Input, ALL
import dash_leaflet as dl
import pandas as pd
import requests

json_data = requests.get("http://128.32.234.154:8800/api/wzd/events/id").json()

df = pd.DataFrame(json_data)

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Zone Mapping App', style={'textAlign':'center'}),
    dcc.Dropdown(df.ids.unique(), 'Canada', id='dropdown-selection'),
    html.Script(src=app.get_asset_url('custom_leaflet.js')),
    dl.Map(
        id="work-zone-map",
        style={'width': '1500px', 'height': '800px'},
        center=[37.8715, -122.2730],  # Initial center
        zoom=5,  # Initial zoom
        children=[
            dl.TileLayer()
        ]
    ),
    dcc.Store(id='coordinates-store', data={'lat': [], 'lon': []})
])

@callback(
    Output('work-zone-map', 'children'),
    Input('dropdown-selection', 'value')
)
def update_map(value):
    geo_json_data = requests.get("http://128.32.234.154:8800/api/wzd/events/" + value).json()
    coords = geo_json_data['geometry']['coordinates']
    longs = [coord[0] for coord in coords]
    lats = [coord[1] for coord in coords]

    polyline = dl.Polyline(positions=list(zip(lats, longs)))
    
    external_css = "https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css"
    icon = dict(
        html='<div><span> 10 </span></div>',
        className='marker-cluster marker-cluster-small',
        iconSize=[40, 40]
    )

    markers = [
        dl.Marker(center=[lat, lon],
                       radius=5,  # Adjust radius as needed
                       color="blue",  # Adjust color as needed
                       id={"type": "marker", "index": i},
                       interactive=True)
        for i, (lat, lon) in enumerate(zip(lats, longs))
    ]

    return [
        dl.TileLayer(),
        polyline,  # Add the polyline
        *circle_markers  # Add the circle markers
        ]

@callback(
    Output('coordinates-store', 'data'),
    Input({'type': 'marker', 'index': ALL}, 'position')
)
def update_coordinates(positions):
    lats = [position[0] for position in positions]
    lons = [position[1] for position in positions]
    return {'lat': lats, 'lon': lons}

if __name__ == '__main__':
    app.run_server(debug=True)