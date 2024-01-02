<h1> Weather report data pipeline </h1>

Weather report data pipeline is a end to end data pieline which collects weather data of indian cities and stores them in mysql database. to collect the data first we generate a random city name using faker then we use geopy to get latitude and longitude of that city later we use openweather api to get weather data.
I have implemented the code in 3 different ways
1. Standanole python code which retrieves weather data and stores it in mysql
2. Kafka python code to retrieves weather data for every millisecond and store it in mysql database
3. automate using airflow
   
<h2><a href="https://pypi.org/project/Faker/">FAKER </a> package</h2>
Faker is a Python package that generates fake data for you. Whether you need to bootstrap your database, create good-looking XML documents, fill-in your persistence to stress test it, or anonymize data taken from a production service, Faker is for you.
We are using faker for generating city names for getting weather report

#### Installation 
```
pip install Faker
```
  ###### Setting up faker to get indian city names
  ```
  #faker to get indian city names
  from faker import Faker</br>
  fake = Faker("en_IN")

  print(fake.city())
  ```
  * for more info : <a href="https://pypi.org/project/Faker/">FAKER</a>
 ## Geopy package 
 geopy is a Python client for several popular geocoding web services.

geopy makes it easy for Python developers to locate the coordinates of addresses, cities, countries, and landmarks across the globe using third-party geocoders and other data sources.

geopy is tested against CPython (versions 3.7, 3.8, 3.9, 3.10, 3.11, 3.12) and PyPy3. geopy 1.x line also supported CPython 2.7, 3.4 and PyPy2.

#### Installation
```
pip install geopy
```
### Geocoders
Each geolocation service you might use, such as Google Maps, Bing Maps, or Nominatim, has its own class in geopy.geocoders abstracting the service’s API. Geocoders each define at least a geocode method, for resolving a location from a string, and may define a reverse method, which resolves a pair of coordinates to an address. Each Geocoder accepts any credentials or settings needed to interact with its service, e.g., an API key or locale, during its initialization.

##### To geolocate a query to an address and coordinates:
```
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="specify_your_app_name_here")
location = geolocator.geocode("175 5th Avenue NYC")
print(location.address)
Flatiron Building, 175, 5th Avenue, Flatiron, New York, NYC, New York, ...
print((location.latitude, location.longitude))
(40.7410861, -73.9896297241625)
print(location.raw)
{'place_id': '9167009604', 'type': 'attraction', ...}
```
##### To find the address corresponding to a set of coordinates:
```
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="specify_your_app_name_here")
location = geolocator.reverse("52.509669, 13.376294")
print(location.address)
Potsdamer Platz, Mitte, Berlin, 10117, Deutschland, European Union
print((location.latitude, location.longitude))
(52.5094982, 13.3765983)
print(location.raw)
{'place_id': '654513', 'osm_type': 'node', ...}
```
<b>For more details on Geopy</b>
  
<b>Documentation</b> : https://geopy.readthedocs.io/

<b>Source Code</b> : https://github.com/geopy/geopy

<b>Stack Overflow</b> : https://stackoverflow.com/questions/tagged/geopy

<b>GIS Stack Exchange</b> : https://gis.stackexchange.com/questions/tagged/geopy

<b>Discussions</b> : https://github.com/geopy/geopy/discussions

<b>Issue Tracker</b> : https://github.com/geopy/geopy/issues

<b>PyPI</b> : https://pypi.org/project/geopy/

 <h2><a href="https://openweathermap.org/current">OpenWeatherAPI</a></h2> 

 
### Call current weather data
#### How to make an API call
###### API call

<hr>

```
https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API key}
```

##### Parameters
<hr>

 ```lat```	&nbsp;&nbsp; <span color = #8a8a8a>required</span>&nbsp;&nbsp;	<span>Latitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API</span><hr>
 <span>```lon```</span>	&nbsp;&nbsp;<span >required</span>&nbsp;&nbsp;	<span>Longitude. If you need the geocoder to automatic convert city names and zip-codes to geo coordinates and the other way around, please use our Geocoding API</span><hr>
 <span>```appid```</span>&nbsp;&nbsp;	<span>required</span>&nbsp;&nbsp;	<span>Your unique API key (you can always find it on your account page under the "API key" tab)</span><hr>
 <span>```mode```</span>&nbsp;&nbsp;	<span>optional</span>	&nbsp;&nbsp;<span>Response format. Possible values are xml and html. If you don't use the mode parameter format is JSON by default. </span><hr>
 <span>```units```</span>	&nbsp;&nbsp;<span>optional</span>	&nbsp;&nbsp;<span>Units of measurement. standard, metric and imperial units are available. If you do not use the units parameter, standard units will be applied by default.</span><hr>
<span>```lang```</span>	&nbsp;&nbsp;<span>optional</span>&nbsp;&nbsp;	<span>You can use this parameter to get the output in your language.</span><hr>

```
Please use Geocoder API if you need automatic convert city names and zip-codes to geo coordinates and the other way around.

Please note that built-in geocoder has been deprecated. Although it is still available for use, bug fixing and updates are no longer available for this functionality.
```

### API response
If you do not see some of the parameters in your API response it means that these weather phenomena are just not happened for the time of measurement for the city or location chosen. Only really measured or calculated data is displayed in API response.
##### JSON
```
JSON format API response example


                          

{
  "coord": {
    "lon": 10.99,
    "lat": 44.34
  },
  "weather": [
    {
      "id": 501,
      "main": "Rain",
      "description": "moderate rain",
      "icon": "10d"
    }
  ],
  "base": "stations",
  "main": {
    "temp": 298.48,
    "feels_like": 298.74,
    "temp_min": 297.56,
    "temp_max": 300.05,
    "pressure": 1015,
    "humidity": 64,
    "sea_level": 1015,
    "grnd_level": 933
  },
  "visibility": 10000,
  "wind": {
    "speed": 0.62,
    "deg": 349,
    "gust": 1.18
  },
  "rain": {
    "1h": 3.16
  },
  "clouds": {
    "all": 100
  },
  "dt": 1661870592,
  "sys": {
    "type": 2,
    "id": 2075663,
    "country": "IT",
    "sunrise": 1661834187,
    "sunset": 1661882248
  },
  "timezone": 7200,
  "id": 3163858,
  "name": "Zocca",
  "cod": 200
}                        
```
                        
<section id="fields_json">
               <p class="sub-header">JSON format API response fields</p> 
               <ul class="docs-list">
                  <li>
                     <code>coord</code>
                     <ul>
                        <li><code>coord.lon</code> Longitude of the location</li>
                        <li><code>coord.lat</code> Latitude of the location</li>
                     </ul>
                  </li>
                  <li>
                     <code>weather</code> (more info <a target="_blank" href="/weather-conditions">Weather condition codes</a>)
                     <ul>
                        <li><code>weather.id</code> Weather condition id</li>
                        <li><code>weather.main</code> Group of weather parameters (Rain, Snow, Clouds etc.)</li>
                        <li><code>weather.description</code> Weather condition within the group. Please find more <a href="#list"> here.</a> You can get the output in your language. <a href="#multi">Learn more</a></li>
                        <li><code>weather.icon</code> Weather icon id</li>
                     </ul>
                  </li>
                  <li><code>base</code> Internal parameter
                  </li>
                  <li>
                     <code>main</code>
                     <ul>
                        <li><code>main.temp</code> Temperature. Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit </li>
                        <li><code>main.feels_like</code> Temperature. This temperature parameter accounts for the human perception of weather. Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit </li>
                        <li><code>main.pressure</code> Atmospheric pressure on the sea level, hPa</li>
                        <li><code>main.humidity</code> Humidity, %</li>
                        <li><code>main.temp_min</code> Minimum temperature at the moment. This is minimal currently observed temperature (within large megalopolises and urban areas). Please find more info <a href="#min">here.</a> Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit</li>
                        <li><code>main.temp_max</code> Maximum temperature at the moment. This is maximal currently observed temperature (within large megalopolises and urban areas). Please find more info <a href="#min">here.</a> Unit Default: Kelvin, Metric: Celsius, Imperial: Fahrenheit</li>
                        <li><code>main.sea_level</code> Atmospheric pressure on the sea level, hPa</li>
                        <li><code>main.grnd_level</code> Atmospheric pressure on the ground level, hPa</li>
                     </ul>
                  </li>
                  <li><code>visibility</code> Visibility, meter. The maximum value of the visibility is 10 km</li>
                  <li>
                     <code>wind</code>
                     <ul>
                        <li><code>wind.speed</code> Wind speed. Unit Default: meter/sec, Metric: meter/sec, Imperial: miles/hour</li>
                        <li><code>wind.deg</code> Wind direction, degrees (meteorological)</li>
                        <li><code>wind.gust</code> Wind gust. Unit Default: meter/sec, Metric: meter/sec, Imperial: miles/hour</li>
                     </ul>
                  </li>
                  <li>
                     <code>clouds</code>
                     <ul>
                        <li><code>clouds.all</code> Cloudiness, %</li>
                     </ul>
                  </li>
                  <li>
                     <code>rain</code>
                     <ul>
                        <li><code>rain.1h</code> <span class="sub">(where available)</span> Rain volume for the last 1 hour, mm. Please note that only mm as units of measurement are available for this parameter </li>
                        <li><code>rain.3h</code> <span class="sub">(where available)</span> Rain volume for the last 3 hours, mm. Please note that only mm as units of measurement are available for this parameter </li>
                     </ul>
                  </li>
                  <li>
                     <code>snow</code>
                     <ul>
                        <li><code>snow.1h</code><span class="sub">(where available)</span> Snow volume for the last 1 hour, mm. Please note that only mm as units of measurement are available for this parameter </li>
                        <li><code>snow.3h</code> <span class="sub">(where available)</span>Snow volume for the last 3 hours, mm. Please note that only mm as units of measurement are available for this parameter </li>
                     </ul>
                  </li>
                  <li><code>dt</code> Time of data calculation, unix, UTC
                  </li>
                  <li>
                     <code>sys</code>
                     <ul>
                        <li><code>sys.type</code> Internal parameter</li>
                        <li><code>sys.id</code> Internal parameter</li>
                        <li><code>sys.message</code> Internal parameter</li>
                        <li><code>sys.country</code> Country code (GB, JP etc.)</li>
                        <li><code>sys.sunrise</code> Sunrise time, unix, UTC</li>
                        <li><code>sys.sunset</code> Sunset time, unix, UTC</li>
                     </ul>
                  </li>
                  <li><code>timezone</code> Shift in seconds from UTC
                  </li>
                  <li><code>id</code> <span style="color:#8C8C8D">City ID. Please note that built-in geocoder functionality has been deprecated. Learn more <a href="#builtin">here</a></span>
                  </li>
                  <li><code>name</code> <span style="color:#8C8C8D">City name. Please note that built-in geocoder functionality has been deprecated. Learn more <a href="#builtin">here</a></span>
                  </li>
                  <li><code>cod</code> Internal parameter
                  </li>
               </ul>
            </section>
