import re

def format_into_geojson(id, core_details, geometry, work_zone_data):
    
    formatted_geojson = {
        'id': id,
        'type': "object",
        "properties": {
            "core-details": {
                "id": core_details[2],
                "type": core_details[1],
                "properties": {
                    "properties": {
                        "core_details": {
                            "road_names": core_details[3],
                            "direction": core_details[4],
                            "name": core_details[5],
                            "description": core_details[6],
                            "creation_date": core_details[7],
                            "update_date": core_details[8]
                        }
                    }
                }
            }
        },
        'geometry': {
            "type": get_wkt_type(geometry[0]),
            "coordinates": get_geometry_cord(geometry[0])
        },
        'definitions': {
            'Work Zone Road Event': {
                'properties': {
                    'start_date': work_zone_data[1],
                    'end_date': work_zone_data[2],
                    'is_start_date_verified': work_zone_data[3],
                    'is_end_date_verified': work_zone_data[4],
                    'is_start_position_verified': work_zone_data[5],
                    'is_end_position_verified': work_zone_data[6],
                    'work_zone_type': work_zone_data[7],
                    'location_method': work_zone_data[8],
                    'vehicle_impact': work_zone_data[9],
                    'beginning_cross_street': work_zone_data[10],
                    'ending_cross_street': work_zone_data[11],
                    'beginning_milepost': work_zone_data[12],
                    'ending_milepost': work_zone_data[13],
                    'reduced_speed_limit_kph': work_zone_data[14]
                }
            }
        }
    }
    
    return formatted_geojson

def get_wkt_type(geometry):
    wkt_type = geometry.partition("(")[0]
    if wkt_type == "LINESTRING":
        return "LineString"
    elif wkt_type == "MULTIPOINT":
        return "MultiPoint"
    elif wkt_type == "POINT":
        return "Point"
    elif wkt_type == "MULTILINESTRING":
        return "MultiLineString"
    else:
        return "UnknownType"

def get_geometry_cord(geometry):
    idx1 = geometry.find("(")
    idx2 = geometry.rfind(")")
    wkt_type = geometry.partition("(")[0]
    
    coord_str = geometry[idx1 + 1:idx2]
    coord_str = re.sub("[()]", "", coord_str)
    coordinates = []
    array_values = []

    array_values = re.split(r",", coord_str)
    
    for idx, value in enumerate(array_values):
        x, y = value.split()
        coordinates.append([float(x), float(y)])
    
    return coordinates








#==============================================================================
# Main function - for standalone execution.
#==============================================================================

def main(argv):
    geom1 = "LINESTRING(-121.8134839 37.3398993,-121.8150591 37.3393793)"
    geom2 = "MULTIPOINT((-121.866188 37.353966),(-121.866188 37.353966))"

    coord = get_geometry_cord(geom2)

    print(coord)



if __name__ == "__main__":
    main(None)