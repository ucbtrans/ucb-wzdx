from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import plotly.io as pio

pio.renderers.default = "chrome"

#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')
#us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")
empty_df = pd.DataFrame(columns=['lat', 'lon'])

json_data = requests.get("http://127.0.0.1:8800/api/wzd/events/id").json()

df = pd.DataFrame(json_data)

app = Dash()

fig = px.scatter_map(empty_df, lat="lat", lon="lon") 
fig.update_layout(map_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_layout(map_center={"lat": 37.8715, "lon": -122.2730})

app.layout = [
    html.H1(children='Zone Mapping App', style={'textAlign':'center'}),
    dcc.Dropdown(df.ids.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='Work Zone Map', figure=fig, style={'width': '1500px', 'height': '800px'})
]



@callback(
    Output('Work Zone Map', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    geo_json_data = requests.get("http://127.0.0.1:8800/api/wzd/events/" + value).json()
    coords = geo_json_data['geometry']['coordinates']
    
    lats = [coord[0] for coord in coords]
    longs = [coord[1] for coord in coords]
    
    fig.update_traces(lat=longs, lon=lats)
    
    return fig

if __name__ == '__main__':
    app.run(debug=True)