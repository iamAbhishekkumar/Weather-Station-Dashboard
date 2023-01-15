from machine import Pin, UART
import utime
import time
import urequests
import ujson


gpsModule = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
buff = bytearray(255)

TIMEOUT = False
FIX_STATUS = False

latitude = ""
longitude = ""
satellites = ""
GPStime = ""


def getGPS(gpsModule):
    global FIX_STATUS, TIMEOUT, latitude, longitude, satellites, GPStime

    timeout = time.time() + 10
    while True:
        print(gpsModule.readline())
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


getGPS(gpsModule)

if(FIX_STATUS == True):
    print("Printing GPS data...")
    print(" ")
    print("Latitude: "+latitude)
    print("Longitude: "+longitude)
    print("Satellites: " + satellites)
    print("Time: "+GPStime)
    print("----------------------")

    FIX_STATUS = False

if(TIMEOUT == True):
    print("No GPS data is found.")
    TIMEOUT = False
    # GETTING LOCATION BASED ON IP LOCATION

    response.close()


def getloc():
    url = 'https://api.bigdatacloud.net/data/client-ip'
    apiKey = 'EEtLXfqiwOLYtaPpGuxLfzGzHzzn55TQ'
    ip = urequests.get(
        "https://api.bigdatacloud.net/data/client-ip").json()['ipString']

    geo_url = 'https://api.apilayer.com/ip_to_location/' + ip
    res = urequests.get(geo_url, headers={"apiKey": apiKey})
    return (res['latitude'], res['longitude'])


def postdata():
    url = ""
    lat, long = getloc()
    data = {
        'temp': 0,
        'humidity': 23,
        'atp': 23433,
        'rain': False,
        'lat': lat
        'long': long
    }
    data = ujson.dumps(data)
    urequests.post(url, data=post_data)
