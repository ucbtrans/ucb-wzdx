"""
RESTful API server for WZ data.
"""

import json
from flask import Flask, jsonify, request



app = Flask(__name__)



@app.route('/wzd', methods=['GET'])
def get_wzd():
 return jsonify({'data': "data coming soon..."})





if __name__ == '__main__':
   app.run(port=8800)
