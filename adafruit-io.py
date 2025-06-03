from time import sleep

from Adafruit_IO import Client, Dashboard, Feed, RequestError

import weatherhat
import credentials
import csv

sensor = weatherhat.WeatherHAT()


# Set to your Adafruit IO username.
# (go to https://accounts.adafruit.com to find your username)
ADAFRUIT_IO_USERNAME = credentials.AIO_username

# Set to your Adafruit IO key.
# Remember, your key is a secret,
# so make sure not to publish it when you publish this code!
ADAFRUIT_IO_KEY = credentials.AIO_Key

# We can compensate for the heat of the Pi and other environmental conditions using a simple offset.
# Change this number to adjust temperature compensation!
OFFSET = -7.5

# Create an instance of the REST client.
aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Create new feeds

# Commented out all wind and rain related sensors - don't have these sensors

try:
    aio.create_feed(Feed(name="Temperature"))
    aio.create_feed(Feed(name="Relative Humidity"))
    aio.create_feed(Feed(name="Pressure"))
    aio.create_feed(Feed(name="Light"))
    '''aio.create_feed(Feed(name="Wind Speed"))
    aio.create_feed(Feed(name="Wind Direction"))
    aio.create_feed(Feed(name="Rain"))'''
    print("Feeds created!")
except RequestError:
    print("Feeds not created - perhaps they already exist?")

temperature_feed = aio.feeds('temperature')
humidity_feed = aio.feeds('relative-humidity')
pressure_feed = aio.feeds('pressure')
light_feed = aio.feeds('light')
'''windspeed_feed = aio.feeds('wind-speed')
winddirection_feed = aio.feeds('wind-direction')
rain_feed = aio.feeds('rain')'''

# Create new dashboard
try:
    dashboard = aio.create_dashboard(Dashboard(name="Weather Dashboard"))
    print("Dashboard created!")
except RequestError:
    print("Dashboard not created - perhaps it already exists?")

dashboard = aio.dashboards('weather-dashboard')

print("Find your dashboard at: " +
      "https://io.adafruit.com/{0}/dashboards/{1}".format(ADAFRUIT_IO_USERNAME,
                                                          dashboard.key))

# Read the BME280 and discard the initial nonsense readings
sensor.update(interval=10.0)
sensor.temperature_offset = OFFSET
temperature = sensor.temperature
humidity = sensor.relative_humidity
pressure = sensor.pressure
print("Discarding the first few BME280 readings...")
sleep(10.0)

# Read all the sensors and start sending data
from datetime import datetime
from send_to_gsheets import send_to_gsheets
from neon_db_call import neon_db_call

weather_data_list = []
count = 0
id = 8997
while True:
    sensor.update(interval=600.0)
    count += 1
    id += 1

    #wind_direction_cardinal = sensor.degrees_to_cardinal(sensor.wind_direction)
    now = datetime.now()
    temperature = (sensor.temperature * 1.8) + 32
    humidity = sensor.relative_humidity
    pressure = sensor.pressure
    light = sensor.lux
    '''windspeed = sensor.wind_speed
    winddirection = wind_direction_cardinal
    rain = sensor.rain'''

    # strftime() method used to create a string
    # representing the current time.
    currentTime = now.strftime("%d/%m/%Y, %H:%M:%S")

    try:
        aio.send_data(temperature_feed.key, temperature)
        aio.send_data(humidity_feed.key, humidity)
        aio.send_data(pressure_feed.key, pressure)
        aio.send_data(light_feed.key, light)
        '''aio.send_data(windspeed_feed.key, windspeed)
        aio.send_data(winddirection_feed.key, winddirection)
        aio.send_data(rain_feed.key, rain)'''
        

        
        print('Data sent to adafruit.io ' + currentTime)

        line_to_write = [
            id,
            currentTime,
            temperature, 
            humidity,
            pressure,
            light
        ]

        weather_data_list.append(line_to_write)

        # this is where we write to gsheets
        # every 6 intervals 
        if count == 6:
            send_to_gsheets(weather_data_list)
            weather_data_list.clear()
            count = 0
            print('Data sent to gsheet ' + currentTime)
        
        
        # writing data to csv
        file_to_open = 'weather-data.csv'
        csv_file = open(file_to_open, 'a', newline='')
        file_headings = ['id', 'current time', 'temperature', 'humidity', 'pressure', 'light']
        csv_writer = csv.DictWriter(csv_file, fieldnames=file_headings)
        #csv_writer.writeheader()

        line_to_write_csv = {
            'id': id, 
            'current time': currentTime,
            'temperature': temperature, 
            'humidity': humidity,
            'pressure': pressure,
            'light': light
        }

        csv_writer.writerow(line_to_write_csv)

        csv_file.close()
        
        print('Data sent to CSV ' + currentTime)
        

        # put call to neon here
        neon_db_call(line_to_write_csv, now)

    except Exception as e:
        print(e)
    
    
    # leave at least 30 seconds between updates for free Adafruit.io accounts
    sleep(600.0)
