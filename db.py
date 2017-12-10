from flask import Flask
from flask import request
from flask.ext.jsonpify import jsonify
import json

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

def get_display_for_city(city_id):
  conn = connect()
  cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
  # return places of interest joined with city for initial marker population
  cur.execute("SELECT * FROM points_of_interest poi JOIN photo p on p.depicted_poi_name = poi.poi_name where poi.city_id = (%s) and p.url = (SELECT url from photo where poi.poi_name = depicted_poi_name order by popularity DESC limit 1)", (city_id,))
  dict_res = cur.fetchall()
  for instance in dict_res:
      instance['date_taken'] = str(instance['date_taken'])
      instance['time_taken'] = str(instance['time_taken'])
  conn.close()
  return dict_res

def get_city_locs():
  conn = connect()
  cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
  # return initial set of cities with their approimate center latitude and longitude
  cur.execute("SELECT city_name, id, AVG(p.latitude) as latitude, AVG(p.longitude) as longitude FROM city JOIN points_of_interest p on city.id = p.city_id group by city_name, id")
  dict_res = cur.fetchall()
  conn.close()
  return dict_res

@app.route('/get_city_info', methods=['GET'])
def get_city_info():
    return jsonify(get_city_locs())

@app.route('/get_city_photos', methods=['GET'])
def get_city_photos():
    target_city = request.args['city']
    return jsonify(get_display_for_city(target_city))

@app.route('/get_filtered_photos', methods=['GET'])
def get_filtered_photos():
    target_poi = request.args['poi']
    target_time = request.args['time']
    target_season = request.args['season']

    times = None
    months = None

    print target_poi
    print target_time
    print target_season

    if target_season == 'Summer':
        months = (6, 7, 8)
    elif target_season == 'Fall':
        months = (9, 10, 11)
    elif target_season == 'Winter':
        months = (12, 1, 2)
    else:
        months = (3, 4, 5)

    if target_time == 'All':
        hours = tuple(range(0, 24))
    elif target_time == 'Day':
        hours = tuple(range(7, 18))
    else:
        hours = tuple(range(18, 24)) + tuple(range(0, 7))

    conn = connect()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    # return places of interest joined with city for initial marker population
    cur.execute("SELECT * FROM points_of_interest poi JOIN photo p on p.depicted_poi_name = poi.poi_name where poi.poi_name = %s and date_part('month', p.date_taken) in %s and date_part('hour', p.time_taken) in %s order by popularity DESC limit 9", (target_poi, months, hours))
    dict_res = cur.fetchall()
    for instance in dict_res:
        instance['date_taken'] = str(instance['date_taken'])
        instance['time_taken'] = str(instance['time_taken'])
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

if __name__ == '__main__':
    app.run(debug=True, port = 80, host = '0.0.0.0')

