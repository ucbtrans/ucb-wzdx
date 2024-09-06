def format_into_geojson(id, core_details):
    
    
    
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
        }
    }
    
    return formatted_geojson

def 