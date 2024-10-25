import dash_leaflet as dl
from dash import Dash, Input, Output, html
import json

app = Dash(__name__)
app.layout = html.Div(
    [
        dl.Map(
            [dl.TileLayer(), dl.Marker(id="marker", draggable=True, position=(56, 10))],
            id="map",
            style={
                "width": "100%",
                "height": "50vh",
                "margin": "auto",
                "display": "block",
            },
            center=[56, 10],
            zoom=6,
        ),
        html.Div(id="output"),
    ]
)


@app.callback(Output("output", "children"), [Input("marker", "position")])
def print_position(position):
    return json.dumps(position)


if __name__ == '__main__':
    app.run(debug=True)
