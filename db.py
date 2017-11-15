from flask import Flask
from flask import request
from flask import jsonify

import psycopg2
import psycopg2.extras
from psycopg2 import sql

app = Flask(__name__)

def connect():
    try:
        conn = psycopg2.connect("dbname='geolocations' user='power_user' host='localhost' password='password'")
        return conn
    except:
        return None


@app.route('/test', methods=['GET'])
def test():
  conn = connect()
  cur = conn.cursor()
  cur.execute(sql.SQL('INSERT INTO {} VALUES (%s)').format(sql.Identifier('test')), ['lmao'])
  conn.commit()
  conn.close()

  return "Successfully inserted meme."

@app.route('/add_points_of_interest', methods=['POST'])
def add_points_of_interest():
  conn = connect()
  cur = conn.cursor()
  points = request.json
  parsed_points = [(p['Name'], " ".join(p['Type']), p['Description'], p['Latitude'], p['Longitude'], p['City_ID']) for i, p in enumerate(points)]
  args_str = ','.join(cur.mogrify("(%s, %s, %s, %s, %s, %s)", poi) for poi in parsed_points)
  cur.execute("INSERT INTO points_of_interest VALUES "  + args_str)
  conn.commit()
  conn.close()

  return "Successfully inserted points_of_interest."

@app.route('/add_photos', methods=['POST'])
def add_photos():
  conn = connect()
  cur = conn.cursor()
  photos = request.json
  parsed_photos = [(p['URL'], p['Date'], p['Time'], p['Popularity'], p['POI_Name']) for p in photos]

  args_str = ','.join(cur.mogrify("(%s, %s, %s, %s, %s)", photo) for photo in parsed_photos)
  cur.execute("INSERT INTO photo(url, date_taken, time_taken, popularity, depicted_POI_name) VALUES "  + args_str)
  conn.commit()
  conn.close()

  return "Successfully inserted photos."

@app.route('/add_cities', methods=['POST'])
def add_cities():
  conn = connect()
  cur = conn.cursor()
  cities = request.json
  parsed_cities = [(c['ID'], c['Name'], c['Country']) for c in cities]

  args_str = ','.join(cur.mogrify("(%s, %s, %s)", city) for city in parsed_cities)
  cur.execute("INSERT INTO city(id, city_name, country) VALUES "  + args_str)
  conn.commit()
  conn.close()

  return  "Successfully added cities"

@app.route('/get_markers', methods=['GET'])
def get_markers():
  conn = connect()
  cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
  # return places of interest joined with city for initial marker population
  cur.execute("SELECT * FROM points_of_interest JOIN city on city_id = id")
  dict_res = cur.fetchall()
  conn.close()
  return jsonify(dict_res)

@app.route('/get_photo_count', methods=['GET'])
def get_photo_count():
  conn = connect()
  cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
  cur.execute("SELECT count(*) FROM photo")
  dict_res = cur.fetchall()
  conn.close()
  return jsonify(dict_res)

#get route that takes in time, lat long bounding box and returns pictures sorted by popularity for that region, limited to some number
@app.route('/get_photos', methods=['GET'])
def get_photos():
    args = request.args.to_dict()
    lim = args['limit'] or 20
    min_lat = args['min_lat']
    max_lat = args['min_lat']
    min_lng = args['min_lng']
    max_lng = args['max_lng']
    if min_lat is None or max_lat is None or min_lng is None or max_lng is None:
        return None
    #cur.execute("SELECT * FROM")
    conn = connect()
    cur = conn.cursor()

    return jsonify(request.args.to_dict())

if __name__ == '__main__':
    app.run(debug=True, port = 80, host = '0.0.0.0')

