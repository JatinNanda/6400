import json
import requests
import sys
from datetime import datetime

API_KEY = ''
REST_END_POINT = 'http://ec2-54-211-108-192.compute-1.amazonaws.com/add_photos'

def getPhotos(lat, lon, location):
	response = requests.get('https://api.flickr.com/services/rest/?method=flickr.photos.search', params={'api_key':API_KEY, 'lat':lat, 'lon':lon, 'radius':.10, 'format':'json','sort':'interestingness-desc','nojsoncallback':1, 'extras':'date_taken,views', 'per_page' : 100})
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



file_name = sys.argv[1]

with open(file_name) as data_file:
	data = json.load(data_file)

poiList = data

photos = []

for i in range(len(poiList)):
	currentPOI = poiList[i]
	lat = currentPOI['Latitude']
	lon = currentPOI['Longitude']
	photos = getPhotos(lat, lon, currentPOI['Name'])
	response = requests.post(REST_END_POINT,json=photos)
	print(response)
	
#with open("PicData.json", 'w') as output_file:
#	json.dump(photos, output_file)

response = requests.post('http://ec2-54-211-108-192.compute-1.amazonaws.com/add_photos',json=photos)

#print(response)

