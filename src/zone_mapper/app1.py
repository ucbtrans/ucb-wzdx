from dash import Dash, html, dcc, callback, Output, Input
import plotly.graph_objects as go
import pandas as pd
import requests
import plotly.io as pio

pio.renderers.default = "chrome"

json_data = requests.get("http://128.32.234.154:8800/api/wzd/events/id").json()

df = pd.DataFrame(json_data)

app = Dash(__name__)

app.layout = html.Div([
    html.H1(children='Zone Mapping App', style={'textAlign':'center'}),
    dcc.Dropdown(df.ids.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='Work Zone Map', 
              figure=go.Figure([
                  go.Scattergeo(  # Hidden Scattergeo for dragging
                      lat=[], 
                      lon=[],
                      mode='markers',
                      marker={'size': 20, 'color': "maroon"},
                      visible='legendonly'  # Hide from the legend
                  ),
                  go.Scattermap(  # Visible Scattermap for display
                      lat=[], 
                      lon=[],
                      mode='markers',
                      marker={'size': 20, 'color': "maroon"} 
                  )
              ]),
              style={'width': '1500px', 'height': '800px'}, 
              config={'editable': True, 
                      'edits': {'shapePosition': True}}),
    dcc.Store(id='coordinates-store', data={'lat': [], 'lon': []})
])

@callback(
    Output('Work Zone Map', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    geo_json_data = requests.get("http://128.32.234.154:8800/api/wzd/events/" + value).json()
    coords = geo_json_data['geometry']['coordinates']
    longs = [coord[0] for coord in coords]
    lats = [coord[1] for coord in coords]
    
    fig = go.Figure([
        go.Scattergeo(
            lat=lats, 
            lon=longs,
            mode='markers',
            marker={'size': 20, 'color': "maroon"},
            visible='legendonly'
        ),
        go.Scattermap(
            lat=lats, 
            lon=longs,
            mode = 'lines+markers',
            line = dict(width = 10, color = 'red'),
            marker={'size': 20, 'color': "maroon"} 
        )
    ])
    fig.update_layout(
        geo={
            'center': {'lat': lats[0], 'lon': longs[0]}
        },
        map={
            'style': "open-street-map"
        },
        showlegend=False
    )
    return fig

@callback(
    Output('coordinates-store', 'data'),
    Input('Work Zone Map', 'figure')
)
def update_coordinates(figure):
    lats = figure['data'][0]['lat']
    lons = figure['data'][0]['lon']
    
    figure['data'][1]['lat'] = lats
    figure['data'][1]['lon'] = lons
    
    return {'lat': lats, 'lon': lons}

if __name__ == '__main__':
    app.run_server(debug=True)