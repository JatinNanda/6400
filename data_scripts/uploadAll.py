import json
import requests
import sys
import csv
from datetime import datetime

with open('API_keys/poi_keys.json') as key_file:
    API_KEY_SYGIC = json.load(key_file)['key']
with open('API_keys/flickr_keys.json') as key_file:
    API_KEY_FLICKR = json.load(key_file)['key']

REST_END_POINT_CITIES = 'http://ec2-54-211-108-192.compute-1.amazonaws.com/add_cities'
REST_END_POINT_POI = 'http://ec2-54-211-108-192.compute-1.amazonaws.com/add_points_of_interest'
REST_END_POINT_PHOTOS = 'http://ec2-54-211-108-192.compute-1.amazonaws.com/add_photos'

def getPhotos(lat, lon, location):
	response = requests.get('https://api.flickr.com/services/rest/?method=flickr.photos.search', params={'api_key':API_KEY_FLICKR, 'lat':lat, 'lon':lon, 'radius':.10, 'format':'json','sort':'interestingness-desc','nojsoncallback':1, 'extras':'date_taken,views', 'per_page' : 200})
	orig_photos = response.json()['photos']['photo']
	photos = []
	for i in range(len(orig_photos)):
		currentPhoto = orig_photos[i]
		photoDict = {}

		dt = datetime.strptime(currentPhoto['datetaken'], '%Y-%m-%d %H:%M:%S')


		photoDict['POI_Name'] = location
		photoDict['Popularity'] = currentPhoto['views']
		photoDict['Date'] =  dt.strftime('%Y-%m-%d')
		photoDict['Time'] = dt.strftime('%H:%M:%S')
		photoDict['URL'] = 'https://farm{}.staticflickr.com/{}/{}_{}.jpg'.format(currentPhoto['farm'], currentPhoto['server'], currentPhoto['id'], currentPhoto['secret'])

		photos.append(photoDict)

	return photos

cities = []
countries = {}

response = requests.get('https://api.sygictravelapi.com/1.0/en/places/list', params={'level':'city', 'limit':100}, headers={'x-api-key':API_KEY_SYGIC})
data = response.json().get('data').get('places')

for i in range(len(data)):
	#city:4484
	current_city = data[i]
	city_id = int(current_city["id"].split(":")[1])
	#"Misima Island"
	name = current_city["name"]
	#108. Get country name keyed off country id
	country = current_city["name_suffix"]
	if not country:
		continue
	city_dict = {"ID": city_id, "Name": name, "Country": country}
	cities.append(city_dict)

if len(sys.argv) > 1:
	post = sys.argv[1]
	if (post == 'YES'):
		response = requests.post(REST_END_POINT_CITIES,json=cities)
		print(response)


for j in range(len(cities)):

	city = cities[j]['ID']
	num_results = 100

	response = requests.get('https://api.sygictravelapi.com/1.0/en/places/list', params={'parents':'city:' + str(city), 'level':'poi', 'limit':num_results}, headers={'x-api-key':API_KEY_SYGIC})

	data = response.json().get('data').get('places')

	poiList = []

	for i in range(len(data)):
		currentPOI = data[i]
		poiDict = {}
		poiDict['Name'] = currentPOI['name']
		poiDict['Type'] = currentPOI['categories']
		poiDict['Latitude'] = currentPOI['location']['lat']
		poiDict['Longitude'] = currentPOI['location']['lng']
		poiDict['Description'] = currentPOI['perex']
		poiDict['City_ID'] = city

	#	poiDict =  dict((k, data[i][k]) for k in ('name', 'parent_ids', 'location', 'categories', 'perex'))
		poiList.append(poiDict)

		#print(poiList)

	if len(sys.argv) > 2:
			post = sys.argv[2]
			if (post == 'YES'):
				response = requests.post(REST_END_POINT_POI,json=poiList)
				print(response)

	if len(sys.argv) > 3 and sys.argv[3] == 'YES':
		for k in range(len(poiList)):
			photos = []
			currentPOI = poiList[i]
			lat = currentPOI['Latitude']
			lon = currentPOI['Longitude']
			photos = getPhotos(lat, lon, currentPOI['Name'])
			response = requests.post(REST_END_POINT_PHOTOS,json=photos)
			print(response)




