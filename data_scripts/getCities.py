import json
import requests
import sys


with open('API_keys/poi_keys.json') as key_file:
    API_KEY = json.load(key_file)['key']
REST_END_POINT = 'http://ec2-54-211-108-192.compute-1.amazonaws.com/add_cities'

cities = []
countries = {}

response = requests.get('https://api.sygictravelapi.com/1.0/en/places/list', params={'level':'city', 'limit':100}, headers={'x-api-key':API_KEY})
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

with open('CityData.json', 'w') as outfile:
	json.dump(cities, outfile)

if len(sys.argv) > 1:
	post = sys.argv[1]
	if (post == 'YES'):
		response = requests.post(REST_END_POINT,json=cities)
		print(response)



