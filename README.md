# ucb-wzdx
Work Zone Project

The PATH work-zone project aims to create a 


Project Structure:
<pre>
/
├── db                          # WZDX local database file
├── src/    
│   ├── dashcam_tracker/        # Dashcamera CV tracker module         
│   │   ├── ...                 
│   ├── zone_mapper/            # Zone mapping web tool module
│   │   ├── leaflet_app.py      # Web DASH application
|   |   ├── osm_mapper.py       # Work-zone refinement microservice
|   |   ├── zone_refinement.py  # Zone Refinement benchmarker
│   ├── rest_api/               # RESTful API module
│   │   ├── ...                 # API-related files
│   ├── ...                     # Shared source files
├── README            
</pre>
