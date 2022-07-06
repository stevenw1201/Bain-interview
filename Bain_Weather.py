import streamlit as st
import pandas as pd
import json
import requests
import plotly.express as px
from datetime import datetime
import time
import openpyxl
from IPython.core.display import HTML

# set current time for historical data api call
now = int(time.time())

# api key 
api_key = 'd65f0dddeb9c3a05baa8200f4a702725'

# for displaying weather icon purpose
def path_to_image_html(path):
    return '<img src="'+ path + '" width="60" >'

# taking input from website
city = st.text_input("Enter city's full name","")
# create an empty list
city_standardized = []

# making it a list for standardization process
city = city.split()

#standardize the input of the city
for x in city:
	if x.isalpha():
		word = x.lower().capitalize()
		city_standardized.append(word)
# if not alphabetic letter, set input to empty and ask to re-enter
	else:
		city_standardized = ''
		st.markdown('please enter the correct name of the city')
city_standardized = ' '.join(city_standardized)

# use try-except for exceptions in inputs
try:
	# go through the process if input is valid
	if city_standardized != '':
		# current api call 
		current='https://api.openweathermap.org/data/2.5/weather?q='+city_standardized+'&appid='+ api_key

		# requests and load JSON
		r=requests.get(current)
		w_dict_c = r.json()

		city_dict = {}
		# Save corresponding city, lontitude, and latitude 
		city_dict[city_standardized] = w_dict_c['coord']

		# historical api call
		hist = 'https://api.openweathermap.org/data/2.5/onecall/timemachine?lat='+str(city_dict[city_standardized]['lat'])+'&lon='+str(city_dict[city_standardized]['lon'])+'&dt='+str(now)+'&appid='+api_key
		r2 = requests.get(hist)
		w_dict_h = r2.json()

		# output city name, and coordinates	
		st.markdown(f""" * **City** : {city_standardized}
			\n* **Coordinates of Location** : \n\t **Lontitude**: {city_dict[city_standardized]['lon']} \n\t **Latitude**: {city_dict[city_standardized]['lat']} """)

		# output raw JSON data
		st.markdown(f"* **Raw JSON Output(Current)** : \n\t{w_dict_c}")

		st.markdown(f"* **Raw JSON Output(Historical)** : \n\t{w_dict_h}")	

		# create a section for the next display
		data = st.container()
		with data:
			st.header('Data Content in Data Frame')
			# identify necessary columns
			cols = list(w_dict_h['hourly'][0].keys())
			cols2 = list(w_dict_h['hourly'][0]['weather'][0].keys())
			
			# create dictionaries with empty lists from the column names
			table = {}
			for x in range(0,len(cols)-1):
				table[cols[x]] = []
			for y in cols2:
				table[y] = []
			# fill the current data
			for i in range(0,len(cols)-1):
				table[cols[i]].append(w_dict_h['current'][cols[i]])
			# fill the historical data
			for r in range(0,len(w_dict_h['hourly'])):
				for c in range(0,len(cols)-1):
					table[cols[c]].append(w_dict_h['hourly'][r][cols[c]])

			# weather data needs to be filled separatedly
			for w in cols2:
				table[w].append(w_dict_h['current']['weather'][0][w])
			for r in range(0,len(w_dict_h['hourly'])):
				for c in cols2:
					table[c].append(w_dict_h['hourly'][r]['weather'][0][c])
			# turn dictionary into dataframe
			df = pd.DataFrame(table)
			# change unix time to date time
			df['dt'] = df['dt'].apply(lambda x: datetime.fromtimestamp(x))

			# create copy for html diplay with icons
			df2 = df.copy()

			# change icon into image addressess
			for i in range(0,len(df2['icon'])):
				df2['icon'][i] = 'http://openweathermap.org/img/wn/'+df['icon'][i]+'@2x.png'
			# display table with icon as image in html format.
			st.write(HTML(df2.to_html(escape=False, formatters=dict(icon=path_to_image_html))))


		# create another section for downloading
		download = st.container()
		with download:
			# create download button
			button = st.button('Download Weather Data in Excel Format')

			st.write(button)

			# if click, download the data in excel format
			if button:
				df.to_excel(city_standardized+' weather.xlsx')
				st.write('Download Complete')
	else:
		st.write('Please Re-enter the correct city name')
except:
	st.write('Please Re-enter the correct city name')

