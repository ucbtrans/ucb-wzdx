import osmnx as osm
from shapely.geometry import Polygon

def create_shapely_polygon(markers):
    return Polygon(markers)

def retrieve_street_graph(markers, sh_polygon):
    min_lat = min(marker[1] for marker in markers)
    max_lat = max(marker[1] for marker in markers)
    min_lon = min(marker[0] for marker in markers)
    max_lon = max(marker[0] for marker in markers)
    
    bbox_p = (max_lat, min_lat, max_lon, min_lon)
    print("Bounding box", bbox_p)
    
    graph = osm.graph_from_bbox(bbox = bbox_p, network_type = 'drive', truncate_by_edge = True)
    return graph

def plot_street_graph(graph):
    osm.plot_graph(graph)
    
def get_street_list_in_bbox(graph):
    return [edge['name'] for edge in graph.edges]