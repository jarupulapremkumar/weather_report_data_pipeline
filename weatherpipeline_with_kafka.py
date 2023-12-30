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
from confluent_kafka import Producer,Consumer
from confluent_kafka.admin import AdminClient 
import socket
import sys
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Process

#setting country as india for faker to give city names only from india
fake = Faker("en_IN")

# calling the Nominatim tool and create Nominatim class
loc = Nominatim(user_agent="WeatherAPI")

#weather Apikey 
openweather_api = '<openweather_api>'

#mysql config
mysql_config = {
  'user': 'root',
  'password': 'root',
  'host': '127.0.0.1',
  'database': 'mydb',
  'raise_on_warnings': True
}

#kafka producer config
kafka_producer_config = {'bootstrap.servers': 'localhost:19092',
        "acks": "all",
        'client.id': socket.gethostname()}


#kafka consumer config
kafka_consumer_config = {'bootstrap.servers': 'localhost:19092',
        'group.id': 'weatherapi_1',
        'auto.offset.reset': 'earliest'}


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




#function for inserting the data to mysql
def insert_values_to_table(final_data):
    #connect to my sql
    cnx = connect_to_mysql(mysql_config, attempts=3)
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


def kafka_producer(config, attempts=3, delay=2):
    attempt = 1

    # Implement a reconnection routine
    while attempt < attempts + 1:
        try:
            return Producer(config)
        except Exception  as err:
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

def delivery_callback(err, msg):
        if err:
            print('ERROR: Message failed delivery: {}'.format(err))
        else:
            print("Produced event to topic {topic}: value = {value:12}".format(
                topic=msg.topic(),value=msg.value().decode('utf-8')))


def message_producer():
    #kafka producer to produce messages
    try:
        producer = kafka_producer(config=kafka_producer_config)
        kafka_broker = {'bootstrap.servers': 'localhost:19092'}
        topic = "weather_topic"
        admin_client = AdminClient(kafka_broker)
        topics_list = admin_client.list_topics().topics
        while True:
            if topic in topics_list.keys():
                #get final data_dict
                producer.produce(topic, value = json.dumps(get_final_data()).encode('utf-8'),callback=delivery_callback)
                # Block until the messages are sent.
                producer.poll(1)
            else:
                print("Exception occurred: kafka broker is down")
                break
    except Exception as err:
        print("Error in producer \n",err)
    finally:
        producer.flush()


def kafka_consumer(config, attempts=3, delay=2):
    attempt = 1

    # Implement a reconnection routine
    while attempt < attempts + 1:
        try:
            return Consumer(config)
        except Exception  as err:
            if (attempts is attempt):
                # Attempts to reconnect failed; returning None
                logger.info("Failed to connect kafka, exiting without a connection: %s", err)
                return None
            logger.info(
                "Connection failed for kafka : %s. Retrying (%d/%d)...",
                err,
                attempt,
                attempts-1,
            )
            # progressive reconnect delay
            time.sleep(delay ** attempt)
            attempt += 1
    return None

def message_consumer():
    
    try:
        consumer = kafka_consumer(kafka_consumer_config)
        kafka_broker = {'bootstrap.servers': 'localhost:19092'}
        topic = "weather_topic"
        admin_client = AdminClient(kafka_broker)
        topics_list = admin_client.list_topics().topics
        consumer.subscribe([topic])
        while True:
            if topic in topics_list.keys():
                msg = consumer.poll(timeout=0.1)
                if msg is None: 
                    continue
                if msg.error():
                    print("ERROR: %s".format(msg.error()))
                else:
                    final_data = json.loads(msg.value().decode('utf-8'))
                    insert_values_to_table(final_data)
            else:
                print("Exception occurred: kafka broker is down")
                break
    except KeyboardInterrupt:
        pass
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()




if __name__ == "__main__":

    print("Started Processing ....")
    
    process_producer = Process(target=message_producer)
    process_consumer = Process(target=message_consumer)

    process_producer.start()
    process_consumer.start()

    process_producer.join()
    process_consumer.join()
    
    '''
    with ProcessPoolExecutor(max_workers=2) as exec:
        exec.submit(message_producer)
        exec.submit(message_consumer)
    '''
    #message_consumer()




