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

fig = go.Figure(go.Scattermap(
    fill = 'toself',
    lon = [],
    lat = [],
    marker = { 'size': 20, 'color': "maroon" },
    mode = 'lines+markers',
    line = dict(width = 10, color = 'red')
    #dragmode = 'select'
)) 
fig.update_layout(map = {
    'style': "open-street-map",
    'center': {'lat': 37.8715, 'lon': -122.2730},
    'zoom': 5},
    showlegend = False)

fig.update_layout(
    clickmode='event+select',
    
)
#fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
#fig.update_layout(center={"lat": 37.8715, "lon": -122.2730})
#fig.add_traces(mode='lines',
#               fill='toself',
#               fillcolor='blue')

app.layout = [
    html.H1(children='Zone Mapping App', style={'textAlign':'center'}),
    dcc.Dropdown(df.ids.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='Work Zone Map', figure=fig, 
              style={'width': '1500px', 'height': '800px'}, 
              config={'editable': True, 
                      'edits': {
                        'shapePosition': True
                    }   
                }
    )
]



@callback(
    Output('Work Zone Map', 'figure'),
    Input('dropdown-selection', 'value')
)
def update_graph(value):
    geo_json_data = requests.get("http://127.0.0.1:8800/api/wzd/events/" + value).json()
    coords = geo_json_data['geometry']['coordinates']
    
    longs = [coord[0] for coord in coords]
    lats = [coord[1] for coord in coords]
    
    fig.update_traces(lat=lats, lon=longs)
    line = dict(width = 3, color = 'blue')
    fig.update_layout(map = {
        'center': {'lat': lats[0], 'lon': longs[0]},
        'zoom': 14})
    #fig.update_layout(dragmode='drawclosedpath')
    
    #fig.add_trace(go.Scatter(
    #        x=lats,
    #        y=longs,
    #       mode='markers',  # Ensure you're in 'markers' mode
    #        marker=dict(size=100)  # Set the desired point size
    #))
    
    return fig

if __name__ == '__main__':
    app.run(debug=True)