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
    return wkt_type

def get_geometry_cord(geometry):
    idx1 = geometry.index("(")
    idx2 = geometry.index(")")
    
    string_values = geometry[idx1 + 1:idx2]
    
    array_values = re.split(r"\s|,", string_values)
    
    for idx, value in enumerate(array_values):
        array_values[idx] = float(value)
    
    return array_values