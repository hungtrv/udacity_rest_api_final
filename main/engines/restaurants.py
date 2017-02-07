from flask import current_app
import googlemaps
import foursquare

def find_restaurant(meal_type, location_string):
	restaurant = None

	gmaps_client_id = current_app.config['GOOGLE_MAPS_CLIENT_ID']
	# gmaps_client_secret = current_app.config['GOOGLE_MAPS_CLIENT_SECRET']
	gmaps = googlemaps.Client( 
			gmaps_client_id
		)

	geocode = gmaps.geocode(location_string)

	if not geocode:
		return restaurant

	latitude = geocode[0]['geometry']['location']['lat']
	longitude = geocode[0]['geometry']['location']['lng']

	foursquare_client_id = current_app.config['FOURSQUARE_CLIENT_ID']
	foursquare_client_secret = current_app.config['FOURSQUARE_CLIENT_SECRET']
	foursquare_client = foursquare.Foursquare(
			client_id=foursquare_client_id,
			client_secret=foursquare_client_secret
		)

	restaurants = foursquare_client.venues.search({
			'll':'{0},{1}'.format(latitude, longitude), 
			'query': meal_type
		})

	if not restaurants['venues']:
		return restaurant

	tmp_restaurant = restaurants['venues'][0]

	return {
			'restaurant_name': tmp_restaurant['name'],
			'restaurant_address': ', '.join(tmp_restaurant['location']['formattedAddress'])
		}

if __name__ == '__main__':
	print find_restaurant('Donuts', 'San Francisco')