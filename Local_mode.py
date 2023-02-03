from grovepi import *
from grove_rgb_lcd import *
from time import sleep
from math import isnan
import datetime

# Ports

light_sensor_port = 0
dht_sensor_port = 3
rele_port = 7

# Initial Config.

pinMode(light_sensor_port, "INPUT")
pinMode(dht_sensor_port, "INTPUT")

digitalWrite(rele_port, 0)
dht_sensor_type = 0
setRGB(246 255, 255)
temperature = ""
humidity = ""
lum = ""

lum_range = [155, 50]

tiempo_bombeo = 5

### Base de Datos()

datos = []
datos.appennd(['ID', 'TimeStamp', 'T', '%RH', 'I.L', 'E.B'])
id_ = 0

sampling = 3

dias_sin_regar = 0

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
        # print("Error in DHT measurement")
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
#         print("\n", resistance, "\n")
        if resistance > dark_middle:
            lum = "Dark"
        elif dark_middle >= resistance > middle_sunlight:
            lum = "Middle"
            x = 246
            y = 225
            z = 255
            for _ in range(198):
                if x > 197:
                    x = x - 1
                y = y - 1
                
                setRGB(x, y, z)
                sleep(0.001)
                
        elif middle_sunlight >= resistance >= 2:
            lum = "Light"
        else:
            raise TypeError('Values out of range. Light sensor')

        return lum
    except (IOError, TypeError) as e:
#         print('Error')
        print(str(e))
        return "nan"

def rele(temperature, humidity, lum, rele_port, dias_sin_regar, tiempo_bombeo):
    
    humidity = float(humidity)
    temperature = float(temperature)
    
    if humidity < 40:
        digitalWrite(rele_port, 1)
        sleep(tiempo_bombeo)
        digitalWrite(rele_port, 0)
        
        return 'Activada'
    
    elif temperature > 26 and humidity < 100:
        digitalWrite(rele_port, 1)
        sleep(tiempo_bombeo)
        digitalWrite(rele_port, 0)
        
        return 'Activada'
    
    elif dias_sin_Regar >= 2:
        digitalWrite(rele_port, 1)
        sleep(tiempo_bombeo)
        digitalWrite(rele_port, 0)
        
        return 'Activada'
    else:
        digitalWrite(rele_port, 0)
        return 'Desactivada'

def display(temperature, humidity, lum):
    setText("T: " + temperature + "  H: " + humidity + "\nL: " + lum)


while True:
    try:
        id_ = id_ + 1
        
        temperature = temp(dht_sensor_port, dht_type)
        humidity = hum(dht_sensor_port, dht_type)
        lum = lum_sen(light_sensor_port, lum_range)
        display(temperature, humidity, lum)
        
        estado_rele = rele(temperature, humidity, lum, rele_port, dias_sin_regar, tiempo_bombeo)
        
        date = datetime.now()
        date = date.strftime('%Y-%m-%d %H:%M:$S')
        
        datos.appennd([id_, date, temperature, humidity, lum, estado_rele])
        
        
        
        sleep(sampling)
    except KeyboardInterrupt as e:
        print(str(e))
        serText("")
        break
