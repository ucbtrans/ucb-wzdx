from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import requests

#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv')

json_data = requests.get("http://127.0.0.1:8800/api/wzd/events/id").json()

df = pd.DataFrame(json_data)

app = Dash()

app.layout = [
    html.H1(children='Title of Dash App', style={'textAlign':'center'}),
    dcc.Dropdown(df.ids.unique(), 'Canada', id='dropdown-selection'),
    dcc.Graph(id='graph-content')
]

#@callback(
#    Output('graph-content', 'figure'),
#    Input('dropdown-selection', 'value')
#)
#def update_graph(value):
#    dff = df[df.country==value]
#    return px.line(dff, x='year', y='pop')

if __name__ == '__main__':
    app.run(debug=True)