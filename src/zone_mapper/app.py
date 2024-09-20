from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import plotly.io as pio

pio.renderers.default = "chrome"

#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')
us_cities = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/us-cities-top-1k.csv")

json_data = requests.get("http://127.0.0.1:8800/api/wzd/events/id").json()

df = pd.DataFrame(json_data)

app = Dash()

fig = px.scatter_map(us_cities, lat="lat", lon="lon", hover_name="City", hover_data=["State", "Population"],
                        color_discrete_sequence=["fuchsia"], zoom=3, height=300)
fig.update_layout(map_style="open-street-map")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.update_layout()

app.layout = [
    html.H1(children='Zone Mapping App', style={'textAlign':'center'}),
    dcc.Dropdown(df.ids.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(figure=fig, style={'width': '1600px', 'height': '800px'})
]



#@callback(
#    Output('graph-content', 'figure'),
#    Input('dropdown-selection', 'value')
#)
#def update_graph(value):
#    geo_json_data = requests.get("http://127.0.0.1:8800/api/wzd/events/id").json()
#    dff = df[df.country==value]
#    return px.line(dff, x='year', y='pop')

if __name__ == '__main__':
    app.run(debug=True)