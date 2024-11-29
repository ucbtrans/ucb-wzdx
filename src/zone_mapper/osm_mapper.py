import osmnx as osm
import geopandas as gpd
from shapely.geometry import Polygon, Point
from shapely import wkt
from pyproj import CRS
import geopandas as gpd
import json


def create_shapely_polygon(markers):
    reversed_markers = [[lon, lat] for lat, lon in markers]
    return Polygon(reversed_markers)

def retrieve_street_graph(markers, sh_polygon):
    
    #print(sh_polygon)
    if not sh_polygon.is_valid:
        print("Polygon is invalid!")    
    
    # Establish CRS zone for UTM
    crs = CRS.from_epsg(4326)
    polygon_proj = gpd.GeoSeries(sh_polygon, crs='epsg:4326').to_crs(crs) 
    point_within_polygon = Point(sh_polygon.centroid.x, sh_polygon.centroid.y) 

    graph = {'edges' : []}
    
    polygon = wkt.loads(sh_polygon.wkt)
    
    try:
        graph = osm.graph.graph_from_polygon(sh_polygon, network_type = 'drive', truncate_by_edge=True)
        print("Success")
    except Exception as e:
        print("No able to produce graph" + repr(e))
        
    print("Graph:", graph)
    return graph

def plot_street_graph(graph):
    osm.plot_graph(graph)
    
def get_street_list_in_graph(graph):
    nodes, edges = osm.graph_to_gdfs(graph, nodes=True, edges=True)
    pretty(edges)
    street_names = set(edges['name'].tolist())
    return street_names

def pretty(d, indent=0):
   with open("edges.json", "w") as f:
    json.dump(d.to_json(), f, indent=4)