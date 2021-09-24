import requests
import datetime
import time
import csv
import sys
from geopy.geocoders import Nominatim
import re
import math
import os

#http://subzerocbd.info/#venues

headers = {
	 'origin': 'https://resy.com',
	 'accept-encoding': 'gzip, deflate, br',
	 'x-origin': 'https://resy.com',
	 'accept-language': 'en-US,en;q=0.9',
	 'authorization': 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
	 'content-type': 'application/x-www-form-urlencoded',
	 'accept': 'application/json, text/plain, */*',
	 'referer': 'https://resy.com/',
	 'authority': 'api.resy.com',
	 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36',
}

def login(username,password):
	data = {
	  'email': username,
	  'password': password
	}


	response = requests.post('https://api.resy.com/3/auth/password', headers=headers, data=data)
	res_data = response.json()
	try:
		auth_token = res_data['token']
	except KeyError:
		print("Incorrect username/password combination")
		sys.exit()
	payment_method_string = '{"id":' + str(res_data['payment_method_id']) + '}'
	return auth_token,payment_method_string

def find_table(res_date,party_size,table_time,auth_token,venue_id):
	#convert datetime to string
	day = res_date.strftime('%Y-%m-%d')
	params = (
	 ('x-resy-auth-token',  auth_token),
	 ('day', day),
	 ('lat', '0'),
	 ('long', '0'),
	 ('party_size', str(party_size)),
	 ('venue_id',str(venue_id)),
	)
	response = requests.get('https://api.resy.com/4/find', headers=headers, params=params)
	data = response.json()
	results = data['results']
	if len(results['venues']) > 0:
		open_slots = results['venues'][0]['slots']
		if len(open_slots) > 0:
			available_times = [(k['date']['start'],datetime.datetime.strptime(k['date']['start'],"%Y-%m-%d %H:%M:00").hour, datetime.datetime.strptime(k['date']['start'],"%Y-%m-%d %H:%M:00").minute) for k in open_slots]

			decimal_available_times = []
			for i in range (0, len(available_times)):
				decimal_available_times.append(available_times[i][1] + available_times[i][2]/60)

			absolute_difference_function = lambda list_value : abs(list_value - table_time)
			decimal_closest_time = min(decimal_available_times, key= absolute_difference_function)
			closest_time = available_times[decimal_available_times.index(decimal_closest_time)][0]

			#closest_time = min(available_times, key=lambda x:abs(x[1]-table_time))[0]
			best_table = [k for k in open_slots if k['date']['start'] == closest_time][0]
			return best_table

def make_reservation(auth_token, payment_method_string, config_id,res_date,party_size):
	#convert datetime to string
	day = res_date.strftime('%Y-%m-%d')
	party_size = str(party_size)
	params = (
		 ('x-resy-auth-token', auth_token),
		 ('config_id', str(config_id)),
		 ('day', day),
		 ('party_size', str(party_size)),
	)
	details_request = requests.get('https://api.resy.com/3/details', headers=headers, params=params)
	details = details_request.json()
	book_token = details['book_token']['value']
	headers['x-resy-auth-token'] = auth_token
	data = {
	  'book_token': book_token,
	  'struct_payment_method': payment_method_string,
	  'source_id': 'resy.com-venue-details'
	}

	response = requests.post('https://api.resy.com/3/book', headers=headers, data=data)


def try_table(day,party_size,table_time,auth_token,restaurantID, restaurantName, payment_method_string,earliest_time, latest_time):
	best_table = find_table(day,party_size,table_time,auth_token,restaurantID)
	if best_table is not None:
			hour = datetime.datetime.strptime(best_table['date']['start'],"%Y-%m-%d %H:%M:00").hour + datetime.datetime.strptime(best_table['date']['start'],"%Y-%m-%d %H:%M:00").minute/60
			if (hour >= earliest_time) and (hour <= latest_time):
				config_id = best_table['config']['token']
				make_reservation(auth_token, payment_method_string,config_id,day,party_size)
				digital_hour= str(int(math.floor(hour))) + ':' + str(int((hour%(math.floor(hour)))*60))
				if(len(digital_hour.split(":")[1]) == 1):
					digital_hour += "0" 
				print ('Successfully reserved a table for ' + str(party_size) + ' at ' + restaurantName + ' at ' + digital_hour)
			else:
				print("No tables will ever be available within that time range")
				time.sleep(5)
			return 1

	else:
		time.sleep(1)
		t = time.localtime()
		current_time = time.strftime("%H:%M:%S", t)
		sys.stdout.write("Waiting for reservations to open up... Current time: " + current_time)
		sys.stdout.flush()
		sys.stdout.write('\r')
		return 0

def readconfig():
	dat = open(os.getcwd() + "/" + 'requests.config').read().split('\n')
	return [k.split('|:')[1] for k in dat]

def gps_venue_id(address,res_date,party_size,auth_token):

	geolocator = Nominatim(user_agent="Me")
	try:
		location = geolocator.geocode(address)
	except AttributeError:
		print("That is an invalid address")


	day = res_date.strftime('%Y-%m-%d')
	params = (
	 ('x-resy-auth-token',  auth_token),
	 ('day', day),
	 ('lat', str(location.latitude)),
	 ('long', str(location.longitude)),
	 ('party_size', str(party_size)),
	)
	print("loading...")
	response = requests.get('https://api.resy.com/4/find', headers=headers, params=params)
	data = response.json()
	
	
	try:
		restaurant_name = re.search('"name": (.*?) "type":', response.text).group(1)
		restaurant_name = re.search('"name": "(.*?)",', restaurant_name).group(1)
		venueID = re.search('{"resy": (.*?)}', response.text).group(1)
		print("Making a booking at " + restaurant_name)
		venueNameandID = [restaurant_name, venueID]
		return(venueNameandID)
	except:
		print("That address is not bookable on Resy")
		time.sleep(5)
		return 0 



def main():
	username, password, address, date, table_time, earliest_time, latest_time, guests = readconfig()
	auth_token,payment_method_string = login(username,password)
	print ('logged in succesfully as ' + username)
	party_size = int(guests)
	table_time = float(table_time.split(":")[0]) + (float(table_time.split(":")[1])/60)
	earliest_time = float(earliest_time.split(":")[0]) + (float(earliest_time.split(":")[1])/60)
	latest_time = float(latest_time.split(":")[0]) + (float(latest_time.split(":")[1])/60)
	if(earliest_time > table_time or latest_time < table_time or earliest_time > latest_time or latest_time < earliest_time):
		print("There was an issue with the times you entered")
		print("Double check to see if the times you entered make sense (Make sure to use military time)")
		time.sleep(5)
		return 0
	day = datetime.datetime.strptime(date,'%m/%d/%Y')
	venueNameandID = gps_venue_id(address,day, party_size, auth_token)
	restaurantName= venueNameandID[0]
	restaurantID = int(venueNameandID[1])
	


	reserved = 0
	while reserved == 0:
		try:
			reserved = try_table(day,party_size,table_time,auth_token,restaurantID, restaurantName, payment_method_string,earliest_time, latest_time)
		except:
			with open('failures.csv','ab') as outf:
				writer = csv.writer(outf)
				writer.writerow([time.time()])
	exit = input("The program executed successfully press anything to exit:")

main()

