import requests
import osm_mapper
import json
from timeout import timeout
import errno
import os
import signal
import functools


@timeout(3, os.strerror(errno.ETIMEDOUT))
def refine_geometry_wrapper(zone_geojson):
    osm_mapper.refine_geometry(zone_geojson)

json_data = requests.get("http://128.32.234.154:8900/api/wzd/events/id").json()

succesful_refinement_count = 0
total_zones = 0

for zone_id in json_data['ids']:
    zone_geojson = requests.get(f"http://128.32.234.154:8900/api/wzd/events/{zone_id}").json()
    
    try:
        refine_geometry_wrapper(zone_geojson)
        succesful_refinement_count+=1
    except Exception as e: print(e)

    
    total_zones += 1
    
    print(succesful_refinement_count / total_zones)

