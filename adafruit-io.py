from time import sleep

from Adafruit_IO import Client, Dashboard, Feed, RequestError

import weatherhat
import credentials

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

while True:
    sensor.update(interval=600.0)

    #wind_direction_cardinal = sensor.degrees_to_cardinal(sensor.wind_direction)

    temperature = (sensor.temperature * 1.8) + 32
    humidity = sensor.relative_humidity
    pressure = sensor.pressure
    light = sensor.lux
    '''windspeed = sensor.wind_speed
    winddirection = wind_direction_cardinal
    rain = sensor.rain'''

    try:
        aio.send_data(temperature_feed.key, temperature)
        aio.send_data(humidity_feed.key, humidity)
        aio.send_data(pressure_feed.key, pressure)
        aio.send_data(light_feed.key, light)
        '''aio.send_data(windspeed_feed.key, windspeed)
        aio.send_data(winddirection_feed.key, winddirection)
        aio.send_data(rain_feed.key, rain)'''
        print('Data sent to adafruit.io')
    except Exception as e:
        print(e)

    # leave at least 30 seconds between updates for free Adafruit.io accounts
    sleep(600.0)
