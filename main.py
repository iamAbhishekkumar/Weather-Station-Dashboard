from machine import Pin, UART, ADC, I2C
import utime
import time
from esp8266 import ESP8266
import ujson
import ure
from bmp280 import *
from dht import DHT11, InvalidChecksum
from time import sleep

gpsModule = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))
buff = bytearray(255)

esp01 = ESP8266()

TIMEOUT = False
FIX_STATUS = False

latitude = ""
longitude = ""
satellites = ""
GPStime = ""

bus = I2C(0,scl=Pin(17),sda=Pin(16),freq=200000)
bmp = BMP280(bus)
bmp.use_case(BMP280_CASE_WEATHER)

Raindrop_AO = ADC(0)

pin = Pin(28, Pin.OUT, Pin.PULL_DOWN)
sensor = DHT11(pin)


def startWifi():
    print("StartUP", esp01.startUP())
    print("Echo-Off", esp01.echoING())

    esp01.setCurrentWiFiMode()

    print("Try to connect with the WiFi..")
    while (1):
        if "WIFI CONNECTED" in esp01.connectWiFi("POCO", "abhishek"):
            print("ESP8266 connect with the WiFi..")
            break
        else:
            print(".")
            time.sleep(2)
            
            
def getGPS(gpsModule):
    global FIX_STATUS, TIMEOUT, latitude, longitude, satellites, GPStime

    timeout = time.time() + 10
    while True:
        buff = str(gpsModule.readline())
        parts = buff.split(',')

        if (parts[0] == "b'$GPGGA" and len(parts) == 15):
            if(parts[1] and parts[2] and parts[3] and parts[4] and parts[5] and parts[6] and parts[7]):
                latitude = convertToDegree(parts[2])
                if (parts[3] == 'S'):
                    latitude = -latitude
                longitude = convertToDegree(parts[4])
                if (parts[5] == 'W'):
                    longitude = -longitude
                satellites = parts[7]
                GPStime = parts[1][0:2] + ":" + \
                    parts[1][2:4] + ":" + parts[1][4:6]
                FIX_STATUS = True
                break

        if (time.time() > timeout):
            TIMEOUT = True
            break
        utime.sleep_ms(500)


def convertToDegree(RawDegrees):

    RawAsFloat = float(RawDegrees)
    firstdigits = int(RawAsFloat/100)
    nexttwodigits = RawAsFloat - float(firstdigits*100)

    Converted = float(firstdigits + nexttwodigits/60.0)
    Converted = '{0:.6f}'.format(Converted)
    return str(Converted)


def getCoord():
    global FIX_STATUS
    getGPS(gpsModule)
    if(FIX_STATUS == True):
        FIX_STATUS = False
        return (latitude, longitude)

    return None

def postDataWithGPS(lat, long, temp, atp, humidity, rain):
    path = f'/postgpsweather?lat={lat}&long={long}&temp={temp}&atp={atp}&humidity={humidity}&rain={rain}'
    statusCode, res = esp01.doHttpGet(
        "http://iotgroup6.pythonanywhere.com",path, "RPi-Pico",port=80)
    res = esp01.doHttpCustom("iotgroup6.pythonanywhere.com", path, "RaspberryPi-Pico",port=80)
    print(res)
    
def postDataWithoutGPS(temp, atp, humidity, rain):
    ip = getip()
    path = f"/postweather?ip={ip}&temp={temp}&atp={atp}&humidity={humidity}&rain={rain}"
    res = esp01.doHttpCustom("iotgroup6.pythonanywhere.com", path, "RaspberryPi-Pico",port=80)
    print(res)

def getip():
    statusCode, res = esp01.doHttpGet("www.httpbin.org","/ip","RaspberryPi-Pico", port=80)
    if statusCode == 200:
        #print(res)
        res = ure.search("{(.*?)\}",res).group(0)
        #print(repr(res))
        res = res.replace("\\n","")
        #print(repr(res))
        res = ujson.loads(res)
        print(res)
        return res['origin']
    
def work():
    temp, humidity = getDHTData()
    atp = getPressure()
    rain = isRain()   
    val = getCoord()
    if val:
        postDataWithGPS(val[0],val[1],temp,atp,humidity,rain)
    else:
        print((temp,atp,humidity,rain))
        postDataWithoutGPS(temp,atp,humidity,rain)

def isRain():
    adc_Raindrop = Raindrop_AO.read_u16()
    if adc_Raindrop < 30000:
        return 1
    else:
        return 0

def getPressure():
    try:
        atp = None
        pressure=bmp.pressure
        atp = pressure / 100
        return atp
    except:
        print("Error in pressuare")
        return 1000

def getDHTData():
    try:
        t  = (sensor.temperature)
        h = (sensor.humidity)
    except:
        t = 25
        h = 70
    return t,h

if __name__ == '__main__':
    startWifi()
    iter = 5
    while iter > 0:
        work()
        sleep(15)
        iter -= 1
    esp01.disconnectWiFi()
    









