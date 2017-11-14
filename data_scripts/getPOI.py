import json
import requests
import sys

#tokyo = 2585
#san francisco = 377
#paris = 14

with open('API_keys/poi_keys.json') as key_file:
    API_KEY = json.load(key_file)['key']
REST_END_POINT = 'http://ec2-54-211-108-192.compute-1.amazonaws.com/add_points_of_interest'

city = sys.argv[1]
num_results = sys.argv[2]

response = requests.get('https://api.sygictravelapi.com/1.0/en/places/list', params={'parents':'city:' + str(city), 'level':'poi', 'limit':num_results}, headers={'x-api-key':API_KEY})

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

print poiList[0]

with open('POIdata.json', 'w') as outfile:
	json.dump(poiList, outfile)

if len(sys.argv) > 3:
	post = sys.argv[3]
	if (post == 'YES'):
		response = requests.post(REST_END_POINT,json=poiList)
		print(response)

