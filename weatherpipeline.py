import requests
import json
import os
from datetime import datetime
from faker import Faker
from geopy.geocoders import Nominatim
from pytz import timezone
import mysql.connector as mysqlconn
import logging
import time

#setting country as india for faker to give city names only from india
fake = Faker("en_IN")

# calling the Nominatim tool and create Nominatim class
loc = Nominatim(user_agent="WeatherAPI")

#weather Apikey 
openweather_api = '<openweather_api>'

#mysql config
config = {
  'user': 'root',
  'password': 'root',
  'host': '127.0.0.1',
  'database': 'mydb',
  'raise_on_warnings': True
}


# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Log to console
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

#function to get random city name
def get_city():
    return fake.city()


#function to get lat and long for city
def get_lat_lon_address_from_city(city):
    # entering the location name
    getLoc = loc.geocode(city)
    return (getLoc.latitude,getLoc.longitude,getLoc.address)

# weatherAPI for collecting weather report for lat and long provided
def get_weather_data(lat,lon,apikey):
    api_url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={apikey}&units=metric'
    return requests.get(api_url)


#function for generating the final data that is inserted into mysql table
def get_final_data():
    final_data = {}

    #getting the random city name using faker 
    city = get_city()

    #getting the lat , long , address
    latitude,longitude,address = get_lat_lon_address_from_city(city)

    #getting the response of openweatherAPI
    response = get_weather_data(latitude,longitude,openweather_api)

    #final data dict
    final_data = {
    "datetime":datetime.now(timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S") ,
    "latitude":latitude,
    "longitude ": longitude,
    "city": city,
    "address": address,
    "weather":response.json()['weather'][0]['description'],
    "tempature" : response.json()['main']['temp'],
    "temp_min" : response.json()['main']['temp_min'],
    "temp_max" : response.json()['main']['temp_max'],
    "humidity" : response.json()['main']['humidity'],
    "report_generation_time": datetime.fromtimestamp(response.json()['dt']).strftime("%Y-%m-%d %H:%M:%S"),
    "cloudiness": response.json()['clouds']['all'],
    "country" : response.json()['sys']['country'],
    "sunrise_time": datetime.fromtimestamp(response.json()['sys']['sunrise']).strftime("%Y-%m-%d %H:%M:%S"), ##convert to localtimezone
    "sunset_time": datetime.fromtimestamp(response.json()['sys']['sunset']).strftime("%Y-%m-%d %H:%M:%S"), ##convert to localtimezone
    }

    return final_data

def get_mysql_connector():
    mydb = mysqlconn.connect(
        host="localhost",
        user="root",
        password="root",
        database="mydb"
    )
    return mydb

#configuring or connecting to mysql
def connect_to_mysql(config, attempts=3, delay=2):
    attempt = 1

    # Implement a reconnection routine
    while attempt < attempts + 1:
        try:
            return mysqlconn.connect(**config)
        except (mysqlconn.Error, IOError) as err:
            if (attempts is attempt):
                # Attempts to reconnect failed; returning None
                logger.info("Failed to connect, exiting without a connection: %s", err)
                return None
            logger.info(
                "Connection failed: %s. Retrying (%d/%d)...",
                err,
                attempt,
                attempts-1,
            )
            # progressive reconnect delay
            time.sleep(delay ** attempt)
            attempt += 1
    return None

def create_mysql_table():

    mydb = get_mysql_connector()

    mycursor = mydb.cursor()
    create_table_query = """
        CREATE TABLE IF NOT EXISTS weather_report (
        datetime DATETIME,
        latitude DOUBLE,
        longitude DOUBLE,
        city varchar(50),
        address varchar(200),
        weather varchar(50),
        tempature FLOAT,
        temp_min FLOAT,
        temp_max FLOAT,
        humidity INT,
        report_generation_time  DATETIME,
        cloudiness INT,
        country VARCHAR(5),
        sunrise_time DATETIME,
        sunset_time DATETIME
        )
    """
    mycursor.execute(create_table_query)


#function for inserting the data to mysql
def insert_values_to_table(final_data):
    #connect to my sql
    cnx = connect_to_mysql(config, attempts=3)
    create_table_query = """
        CREATE TABLE IF NOT EXISTS weather_report (
        datetime DATETIME,
        latitude DOUBLE,
        longitude DOUBLE,
        city varchar(50),
        address varchar(200),
        weather varchar(50),
        tempature FLOAT,
        temp_min FLOAT,
        temp_max FLOAT,
        humidity INT,
        report_generation_time  DATETIME,
        cloudiness INT,
        country VARCHAR(5),
        sunrise_time DATETIME,
        sunset_time DATETIME
        )
    """
    #run SQL Queries
    if cnx and cnx.is_connected():
        with cnx.cursor() as cursor:
            cursor.execute('SHOW Tables')
            myresult = cursor.fetchall()
            if 'weather_report' not in [table[0] for table in myresult]:
                cursor.execute(create_table_query)
            else:
                cursor.execute(f"INSERT INTO weather_report ({ ','.join(list(final_data.keys())) }) VALUES {str(tuple(final_data.values()))}")
            cnx.commit()
            print("inserted data suceesfully at ",datetime.now(timezone('Asia/Kolkata')).strftime("%Y-%m-%d %H:%M:%S"))
        cnx.close()
    else:
        print("Could not connect to mysql")


def get_minute_weather_report():
    #calls the api for every 1 minute
    print("data will be inserted for every 1 minute")
    while True:
        insert_values_to_table(get_final_data())
        time.sleep(60)

def get_x_minute_weather_report(x: int):
    #calls the api for every x  minute
    print(f"data will be inserted for every {int(x)} minutes")
    while True:
        insert_values_to_table(get_final_data())
        time.sleep(60*x)



def get_hourly_weather_report():
    #calls the api for every 1 hour
    print("data will be inserted for every 1 hour")
    last_process_time=time.time()
    insert_values_to_table(get_final_data())
    while True:
        if (time.time() - last_process_time >= (60*60)):
            insert_values_to_table(get_final_data())
            last_process_time=time.time()


def get_x_hourly_weather_report(x: int):
    #calls the api for every x hour
    print(f"data will be inserted for every {int(x)} hours")
    last_process_time=time.time()
    insert_values_to_table(get_final_data())
    while True:
        if (time.time() - last_process_time >= (60*60*x)):
            insert_values_to_table(get_final_data())
            
            last_process_time=time.time()

if __name__ == "__main__":

    print("Started Processing ....")
    get_x_minute_weather_report(5)




