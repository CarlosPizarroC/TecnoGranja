from grovepi import *
from grove_rgb_lcd import *
from time import sleep
from math import isnan

# Ports

light_sensor_port = 0
dht_sensor_port = 3

# Initial Config.

pinMode(light_sensor_port, "INPUT")
pinMode(dht_sensor_port, "INTPUT")

dht_type = 0
setRGB(0 255, 0)
temperature = ""
humidity = ""
lum = ""

lum_range = [400, 30]

####################

def hum(dht_port, dht_type):
    try:
        [_, h] = dht(dht_port, dht_type)
        if isnan(h):
            raise TypeError('nan Error. DHT sensor: hum')
        
        humidity = str(h)
        return humidity
    except (IOError, TypeError) as e:
        print(str(e))
        setText("")

def temp(dht_port, dht_type):
    try:
        [t, _] = dht(dht_port, dht_type)
        if isnan(t):
            raise TypeError('nan Error. DHT sensor: temp')
        
        temperature = str(t)
        return temperature
    except (IOError, TypeError) as e:
        print(str(e))
        setText("")

def lum_sen(lum_port, lum_range):
    try:

        dark_middle = lum_range[0]
        middle_sunlight = lum_range[1]
        sensor_value = analogRead(lum_port)

        if isnan(sensor_value):
            raise TypeError('nan Error. Light sensor')

        resistance = (float)((1023 - sensor_value) * 68) / sensor_value
        print("\n", resistance, "\n")
        if 100 >= resistance > dark_middle:
            lum = "Dark"
        elif dark_middle >= resistance > middle_sunlight:
            lum = "Middle"
        elif middle_sunlight >= resistance >= 0:
            lum = "Light"
        else:
            raise TypeError('Values out of range. Light sensor')

        return lum
    except (IOError, TypeError) as e:
        print(str(e))
        return "nan"

def rele():
    pass

def display(temperature, humidity, lum):
    setText("T: " + temperature + "  H: " + humidity + "\nL: " + lum)


while True:
    try:
        temperature = temp(dht_sensor_port, dht_type)
        humidity = hum(dht_sensor_port, dht_type)
        lum = lum_sen(light_sensor_port, lum_range)
        display(temperature, humidity, lum)

        sleep(0.5)
    except KeyboardInterrupt as e:
        print(str(e))
        serText("")
        break