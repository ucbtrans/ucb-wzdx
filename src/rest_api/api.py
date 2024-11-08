"""
RESTful API server for WZ data.
"""
import os
from dotenv import find_dotenv, load_dotenv
import json
import mysql.connector
from flask import Flask, jsonify, request, g
from shapely import wkb
from geojson_formatter import format_into_geojson
from tools.db_routines import update_road_event


dotenv_path = find_dotenv()
load_dotenv(dotenv_path)


app = Flask(__name__)

def get_db():
   '''
   Create singleton instance of the connection object to the database
   
   :return: DB connector object
   '''
   if 'db' not in g:
      #g.db = mysql.connector.connect(
      #   host=os.getenv('HOST'), 
      #   port=int(os.getenv('PORT')), 
      #   database=os.getenv('DATABASE'), 
      #   user=os.getenv('USERNAME'), 
      #   password=os.getenv('PASSWORD')
      #)
      g.db = mysql.connector.connect(
         host="localhost", 
         port=3306, 
         database="wzdb", 
         user="root", 
         password="WZDx24"
      )
   return g.db

@app.teardown_appcontext
def close_db(error):
   '''
   Closes the connection after every request, even if an error occurs.
   
   :param: Error object
   '''
   
   db = g.pop('db', None)
   if db is not None:
      db.close()

@app.route('/api/wzd', methods=['GET'])
def get_wzd():
   '''
   Test Flask route for GET request
   
   :return: JSON object 
   '''
   
   return jsonify({'data': "data coming soon..."})

@app.route('/api/wzd/events/id', methods=['GET'])
def get_wzd_ids():
   '''
   GET request for all id values
   
   :return: JSON object containing all id Strings
   '''
   
   conn = get_db()
   mycursor = conn.cursor()
   mycursor.execute("SELECT id FROM road_event_feature")
   records = mycursor.fetchall()
   
   ids = {
      'ids' : [r[0] for r in records]
   }
   
   return jsonify(ids)

@app.route('/api/wzd/events/<id>', methods=['GET'])
def get_wzd_record(id):
   '''
   Get the coressponding record in GeoJSON from a dataset given an id string.
   
   :param: id string
   88
   :return: formatted JSON record 
   '''
   
   # To-Do: Format data into GeoJSON format and fix event_feature_data conversion
   
   conn = get_db()
   mycursor = conn.cursor()
   try:
      mycursor.execute("SELECT * FROM road_event_core_details WHERE road_event_feature_id = %s", (id,))
      core_details_data = mycursor.fetchone()
      
      mycursor.execute("SELECT * FROM road_event_feature WHERE id = %s", (id,))
      event_feature_data = mycursor.fetchone()
      
      mycursor.execute("SELECT * FROM work_zone_event WHERE road_event_feature_id = %s", (id,))
      work_zone_data = mycursor.fetchone()
      
      mycursor.execute("SELECT * FROM worker_presence WHERE road_event_feature_id = %s", (id,))
      worker_presence_data = mycursor.fetchone()
      
      mycursor.execute("SELECT * FROM type_of_work WHERE road_event_feature_id = %s", (id,))
      work_type_data = mycursor.fetchone()
      
      mycursor.execute("SELECT ST_AsWKT(geometry) FROM road_event_feature WHERE id = %s and deleted is null", (id,))
      geometry_data = mycursor.fetchone()
      
      #print(len(event_feature_data))
      #converted_event_feature_data = [event_feature_data[0], wkb.loads(bytes(event_feature_data[1])).wkt]
      converted_event_feature_data = [event_feature_data[0], geometry_data[0]]
      
      
      # Put this in another method to format into GeoJSON
      #data = {
      #   'core_details': core_details_data if core_details_data else None,
      #   'event_feature': converted_event_feature_data if event_feature_data else None,
      #   'work_zone': work_zone_data if work_zone_data else None,
      #   'worker_presence': worker_presence_data if worker_presence_data else None,
      #   'type_of_work': work_type_data if work_type_data else None
      #}
      
      data = format_into_geojson(id, core_details_data, geometry_data, work_zone_data)
      
      return jsonify(data)
   except mysql.connector.Error as err:
      return jsonify({'error': str(err)}), 500

@app.route('/api/wzd/events/', methods=['POST'])
def post_wzd_record():
   json = request.get_json()
   
   geometry_type = json['properties']['geometry']['properties']['type']
   geometry_coord = json['properties']['geometry']['properties']['coordinates']
   
   print(geometry_type)
   print(geometry_coord)
   update_road_event(g.db, json, is_new = False)

#if __name__ == '__main__':
#   app.run(host="128.32.234.154", port=8900)

if __name__ == '__main__':
   app.run(port=8800)