import osmnx as osm
import geopandas as gpd
from shapely.geometry import Polygon, Point, LineString
from shapely import wkt
from pyproj import CRS
import geopandas as gpd
import json
import networkx as nx
from shapely.ops import transform
import pyproj
from functools import partial
import re


def create_shapely_polygon(markers):
    reversed_markers = [[lon, lat] for lat, lon in markers]
    return Polygon(reversed_markers)

def retrieve_scaled_street_graph(markers, sh_polygon):
    if not sh_polygon.is_valid:
        print("Polygon is invalid!")    
    
    # Establish CRS zone for UTM
    crs = CRS.from_epsg(4326)
    polygon_proj = gpd.GeoSeries(sh_polygon, crs='epsg:4326').to_crs(crs) 
    point_within_polygon = Point(sh_polygon.centroid.x, sh_polygon.centroid.y) 

    bounded_street_graph = nx.MultiDiGraph()
        
    polygon = wkt.loads(sh_polygon.wkt)
    
    print(list(bounded_street_graph.nodes))
          
    while (list(bounded_street_graph.nodes) == []):
        bounded_street_graph = generate_graph_from_polygon(sh_polygon)
        sh_polygon = sh_polygon.buffer(0.0008)
        print(list(bounded_street_graph.nodes))
         
    print("Graph:", bounded_street_graph)
    return bounded_street_graph

def generate_graph_from_polygon(sh_polygon):
    try:
        graph = osm.graph.graph_from_polygon(sh_polygon, network_type = 'drive', truncate_by_edge=True)
        print("Success")
    except Exception as e:
        print("No able to produce graph: " + repr(e))
        graph = nx.MultiDiGraph()
        
    return graph

def plot_street_graph(graph):
    osm.plot_graph(graph)
    
def get_street_list_in_graph(graph):
    nodes, edges = osm.graph_to_gdfs(graph, nodes=True, edges=True)
    pretty(edges)
    #print("Edges: ", edges)
    #print("Nodes: ", nodes)
    street_names = edges['name']
    flat_street_names = flatten(street_names)
    print(set(flat_street_names))
    return street_names

def pretty(d, indent=0):
    d.to_file("edges.json", driver="GeoJSON") 
    
def flatten(lst):
  flattened = []
  for item in lst:
    if isinstance(item, list):
      flattened.extend(flatten(item))
    else:
      flattened.append(item)
  return flattened

def get_feature(graph, street_name):
    with open('edges.json', 'r') as f:
        geojson_data = json.load(f)
        
    for feature in geojson_data['features']:
        print(feature['properties'].get('name'))
        if feature['properties'].get('name') != None:
            if feature['properties'].get('name').lower().split()[0] == street_name.lower().split()[0]:
                return feature
    else:
        return None
    
def check_first_word_match(str1, str2):
    if not str1.strip() or not str2.strip():  # Check for empty or whitespace-only strings
        return False

    # Use regular expressions for more robust word extraction
    # \b matches word boundaries, \w+ matches one or more word characters
    match1 = re.match(r"\b(\w+)", str1)
    match2 = re.match(r"\b(\w+)", str2)

    if match1 and match2:
        return match1.group(1).lower() == match2.group(1).lower()
    else:
        return False
    
def buffer_linestring_segmentwise(street_line, buffer_dist):
    polygon_points = []
    for i in range(1, len(linestring_coords)):
        p1 = np.array(linestring_coords[i-1])
        p2 = np.array(linestring_coords[i]) 
        
        segment_vector = p2 - p1
        segment_vector = segment_vector / np.linalg.norm(segment_vector)  # Normalize   
        
        
        perpendicular_vector1 = np.array([-segment_vector[1], segment_vector[0]])
        perpendicular_vector2 = -perpendicular_vector1  

        offset_point1 = p1 + buffer_distance * perpendicular_vector1
        offset_point2 = p2 + buffer_distance * perpendicular_vector1
        offset_point3 = p2 + buffer_distance * perpendicular_vector2
        offset_point4 = p1 + buffer_distance * perpendicular_vector2    


        if i == 1:  # First segment
            polygon_points.extend([offset_point1, offset_point2])
        else:
            polygon_points.extend([offset_point2])  # Avoid duplicate points
        polygon_points.append(offset_point3)    
        if i == len(linestring_coords) - 1:  # Last segment
            polygon_points.extend([offset_point4, offset_point1])  # Close the polygon

    return polygon_points


def buffer_linestring_geodesic(linestring_coords, buffer_distance):
    # Define the projection (WGS 84 - common for lat/long)
    wgs84 = pyproj.Proj(init='epsg:4326')  

    # Create a Shapely LineString
    linestring = LineString(linestring_coords)

    # Project to a suitable projected coordinate system (e.g., UTM)
    project_to_utm = partial(
        pyproj.transform,
        pyproj.Proj(init='epsg:4326'),
        pyproj.Proj(proj='utm', zone=utm_zone(linestring_coords[0][0]), ellps='WGS84'),
    )
    utm_linestring = transform(project_to_utm, linestring)

    # Buffer the LineString (distance in meters)
    utm_polygon = utm_linestring.buffer(buffer_distance)

    # Project back to WGS 84 (lat/long)
    project_to_wgs84 = partial(
        pyproj.transform,
        pyproj.Proj(proj='utm', zone=utm_zone(linestring_coords[0][0]), ellps='WGS84'),
        pyproj.Proj(init='epsg:4326'),
    )
    wgs84_polygon = transform(project_to_wgs84, utm_polygon)
    
    simplified_polygon = wgs84_polygon.simplify(tolerance=0.0001)

    # Return the polygon coordinates as a list
    return list(simplified_polygon.exterior.coords)

def utm_zone(longitude):
    return int(longitude // 6) + 31