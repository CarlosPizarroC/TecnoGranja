# Se importan las librerías necesarias:
from grovepi import *           # Para el uso de los sensores (Lumínico, temperatura y humedad).
from grove_rgb_lcd import *     # Para el uso de la pantalla LCD.
from time import sleep          # Para implementar tiempos de espera (sampling, tiempo de bombeo , etc.).
from math import isnan          # Para verificar valores nulos en pro de exponer posibles errores en los sensores.
import datetime                 # Para utilizar las fechas (Registro de muestras, contabilizar días sin regar).

# Declaración de Puertos:

light_sensor_port = 0           # Sensor lumínico.
dht_sensor_port = 3             # Sensor de Temperatura y Humedad.
rele_port = 7                   # Módulo Relé.

# Configuración Inicial:

pinMode(light_sensor_port, "INPUT")
pinMode(dht_sensor_port, "INTPUT")
pinMode(rele_port, "OUTPUT")

digitalWrite(rele_port, 0)
dht_sensor_type = 0
setRGB(246 255, 255)            # Se define una tonalidad del violeta como color inicial (Correspondiente a la intensidad lumínica "Light")
temperature = ""
humidity = ""
lum = "Light"

lum_range = [155, 50]           # Se declaran los valores de la resistancia, producida por el sensor lumínico, que separan las categorías
                                # de intensidad lumínica "Dark", "Middle" y "Light", de la siguiente forma:
                                #
                                #   - lum_range[0] : División Dark-Middle   ;     Es decir lum > lum_range[0] es considerado "Dark").
                                #   - lum_range[1] : División Middle-Light  ;     Es decir lum_range[0] >= lum > lum_range[1] es considerado "Middle").  
                                #                                                 Es decir lum_range[1] >= lum > 2 es considerado "Light").  

DARK_RGB = [119, 0, 200]        # Se define el color en valores RGB que se desea para cada categoría de iluminación.
MIDDLE_RGB = [197, 57, 255]
LIGHT_RGB = [246, 255, 255]
                 
 
tiempo_bombeo = 5               # Aquí se define el tiempo de bombeo como 5 segundos con base a lo requeridos (Este es un valor ejemplo).

# Base de Datos:

## Se inicializa la matriz donde se guardarán las mediciones realizadas cada "sampling" segundos.

datos = []
datos.appennd(['ID', 'TimeStamp', 'T', '%RH', 'I.L', 'E.B'])    
id_ = 0

sampling = 3

horas_sin_regar = 0

# Definición de Función:

def control_RGB(lum_anterior, lum_actual, DARK_RGB, MIDDLE_RGB, 
                LIGHT_RGB):                                         # Función encargada de realizar los cambios en la tonalidad de la pantalla con base
                                                                    # al nivel de iluminación actual.
        
    if lum_anterior != lum_actual and not(lum_anterior == 'nan'):   # Solo realizan cambios si hay cambio en el nivel de iluminación y si no es un valor 'nan'.
        
                                                                    
        if lum_anterior == 'Dark':                                  # Se definen los valores de la tonalidad (RGB) presente y la tonalidad deseada.
            rgb = DARK_RGB
        elif lum_anterior == 'Middle':
            rgb = MIDDLE_RGB
        elif lum_anterior == 'Light':
            rgb = LIGHT_RGB

        if lum_actual == 'Dark':
            rgb_objetivo = DARK_RGB
        elif lum_actual == 'Middle':
            rgb_objetivo = MIDDLE_RGB
        elif lum_actual == 'Light':
            rgb_objetivo = LIGHT_RGB
            
        r = rgb[0]
        g = rgb[1]
        b = rgb[2]
        r_objetivo = rgb_objetivo[0]
        g_objetivo = rgb_objetivo[1]
        b_objetivo = rgb_objetivo[2]
        
        diffs = [r_objetivo - r, g_objetivo - g, b_objetivo - b]                        # Se obtiene la diferencia entre los valores RGB.
        diffs_abs = [abs(r_objetivo - r), abs(g_objetivo - g), abs(b_objetivo - b)]     # Se obtiene el valor absoluto de estas diferencias.
        
        
        indice_max = diffs_abs.index(max(diffs_abs))                                    # Se extrae el indice del valor absoluto más grande
                                                                                        # para así obtener cual es el mayor número de iteraciones
                                                                                        # que serán necesarias para llegar a la tonalidad.
                
        diferencia_max = diffs[indice_max]                                            
        iteraciones = diffs_abs[indice_max]
        
        if diferecia_max < 0:                                                           # Se define si hay que sumar o restar para llegar a las tonalidad
                                                                                        # y se suma o resta de 1 en 1 hasta que cada valor llegue al objetivo.
            
            for _ in range(iteraciones):
                
                if r > r_objetivo:
                    r = r - 1
                if g > g_objetivo:
                    g = g - 1
                if b > b_objetivo:
                    b = b - 1
                    
                setRGB(r, g, b)
                sleep(0.001)
        else:
            
            for _ in range(iteraciones):
                
                if r < r_objetivo:
                    r = r + 1
                if g < g_objetivo:
                    g = g + 1
                if b < b_objetivo:
                    b = b + 1
                 
                setRGB(r, g, b)
                sleep(0.001)
                    

def hum(dht_port, dht_type):                                    # Función para medir la humedad ambiente ó detectar posibles errores en el sensor dht.
    try:
        [_, h] = dht(dht_port, dht_type)
        if isnan(h):
            raise TypeError('nan Error. DHT sensor: hum')
        
        humidity = str(h)
        return humidity
    except (IOError, TypeError) as e:
        print(str(e))
        setText("")

def temp(dht_port, dht_type):                                   # Función para medir la temperatura ambiente ó detectar posibles errores en el sensor dht.
    try:
        [t, _] = dht(dht_port, dht_type)
        if isnan(t):
            raise TypeError('nan Error. DHT sensor: temp')      # Se eleva un error en caso de recibir un valor nan de parte del sensor.
        
        temperature = str(t)
        return temperature
    except (IOError, TypeError) as e:
        print(str(e))
        setText("")

def lum_sen(lum_port, lum_range, lum_anterior, DARK_RGB, MIDDLE_RGB, # Función para medir la iluminación ambiente ó detectar posibles errores en el sensor
            LIGHT_RGB):                                              # y categorizar la intensidad lumínica del momento con base con los rangos anteriormente
                                                                     # definidos anteriormente (lum_range).
    try:
                                                                     
        dark_middle = lum_range[0]
        middle_sunlight = lum_range[1]
        sensor_value = analogRead(lum_port)

        if isnan(sensor_value):                                 
            raise TypeError('nan Error. Light sensor')          # Se eleva un error en caso de recibir un valor nan de parte del sensor.
        resistance = (float)((1023 - sensor_value) * 68) / sensor_value     # Se obtiene el valor de la resistancia.
        
        if resistance > dark_middle:                                        # Se define el rango luminíco (lum) y se llama a la función control_RGB()
                                                                            # para realizar el cambio correspondiente en la tonalidad del display
            control_RGB(lum_anterior, 'Dark', DARK_RGB, MIDDLE_RGB, LIGHT_RGB)                               
            lum = "Dark"
            
        elif dark_middle >= resistance > middle_sunlight:
            control_RGB(lum_anterior, 'Middle', DARK_RGB, MIDDLE_RGB, LIGHT_RGB)
            lum = "Middle"
                
        elif middle_sunlight >= resistance >= 2:
            control_RGB(lum_anterior, 'Light', DARK_RGB, MIDDLE_RGB, LIGHT_RGB)
            lum = "Light"
        else:
            raise TypeError('Values out of range. Light sensor')            # Se eleva un error por medición de valores fuera de rango.

        return lum
    except (IOError, TypeError) as e:

        print(str(e))
        return "nan"

def rele(temperature, humidity, lum, rele_port, horas_sin_regar, tiempo_bombeo):        # Función para la actvación de la bomba de riego por medio del relé.
                                                                                        # Condiciona el riego con base a algunas situaciones 
                                                                                        # (como más de 2 diás sin riego).
    humidity = float(humidity)
    temperature = float(temperature)
    
    estado_bomba = ""
    
    if humidity < 40:
        digitalWrite(rele_port, 1)
        sleep(tiempo_bombeo)
        digitalWrite(rele_port, 0)
        
        horas_sin_regar = 0
        estado_bomba = 'Activada'
    
    elif temperature > 26 and humidity < 100:
        digitalWrite(rele_port, 1)
        sleep(tiempo_bombeo)
        digitalWrite(rele_port, 0)
        
        horas_sin_regar = 0
        estado_bomba = 'Activada'
    
    elif horas_sin_Regar >= 48 and  lum == 'Dark':
        digitalWrite(rele_port, 1)
        sleep(tiempo_bombeo)
        digitalWrite(rele_port, 0)
        
        horas_sin_regar = 0
        estado_bomba = 'Activada'
        
    else:
        digitalWrite(rele_port, 0)
        estado_bomba = 'Desactivada'
        
    return estado_bomba, horas_sin_regar

def display(temperature, humidity, lum):                                    # Función para imprimir los valores principales en el display.
    setText("T: " + temperature + "  H: " + humidity + "\nL: " + lum)


while True:                                                                 # Bucle de funcionamiento.
    try:
        id_ = id_ + 1                                                       # Se aumenta el id de la medición.
                
        temperature = temp(dht_sensor_port, dht_type)                       # Se realizan las mediciones y se imprimen en el display.
        humidity = hum(dht_sensor_port, dht_type)
        lum = lum_sen(light_sensor_port, lum_range, lum, DARK_RGB, MIDDLE_RGB, LIGHT_RGB)
        display(temperature, humidity, lum)
        
        estado_rele, horas_sin_regar = rele(temperature, humidity, lum, rele_port, horas_sin_regar, tiempo_bombeo) # Se ejecuta la función rele() para determinar
                                                                                                                   # la activación de la bomba y resetear el conteo
                                                                                                                   # días sin regar si se realiza un riego.                                                
        
        
        date = datetime.now()                                               # Se obtiene la fecha actual como un objeto de tipo datetime.
        date_str = date.strftime('%Y-%m-%d %H:%M:$S')                       # Se obtiene una string de la fecha con un formato específico.
        
        if id_ > 1:                                                         # Si ya se ha realizado almenos una medición.
            diferencia = date - date_anterior
            diferencia_horas = diferencia.total_seconds() / 3600
            horas_sin_regar = horas_sin_regar + diferencia_horas            # Se aumenta el contador de tiempo sin riego (en horas).
       
        date_anterior = date                                                # Se guarda la fecha tipo datetime para realizar el conteo sin riego en la siguiente 
                                                                            # iteración.
            
        datos.appennd([id_, date_str, temperature, humidity, lum, estado_rele]) # Se guarda la medición en la base de datos.
        
        sleep(sampling)                                                     # Se espera el tiempo de muestreo.
    except KeyboardInterrupt as e:
        print(str(e))
        serText("")
        break
