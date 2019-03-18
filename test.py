# -*- coding: utf-8 -*-
from meteofrance.client import meteofranceClient, meteofranceError
import time


client = meteofranceClient('01700')
client.need_rain_forecast = False
client.update()
print(client.get_data())

exit()

print(client.need_rain_forecast)
client.need_rain_forecast = True
time.sleep(1)
print(client.need_rain_forecast)
client.update()
print(client.get_data())


exit()

client = meteofranceClient('oslo, norvege', True)
print(client.get_data())

exit()

client = meteofranceClient('luxembourg', True)
print(client.get_data())

client = meteofranceClient('01700', True)
print(client.get_data())

exit()

#marseille : no rain forecast
try:
    client = meteofranceClient(13000, True)
    print(client.get_data())
except meteofranceError as exp:
    print(exp)

#Rouen : rain forecast available
try:
    client = meteofranceClient(76000, True)
    print(client.get_data())
except meteofranceError as exp:
    print(exp)

#postal code is not correct : should return the first result which is "Ableiges"
try:
    client = meteofranceClient(95, True)
    print(client.get_data())
except meteofranceError as exp:
    print(exp)

#postal code is a city name : should work anyway with Brest forecast
try:
    client = meteofranceClient("Brest", True)
    print(client.get_data())
except meteofranceError as exp:
    print(exp)

#postal code is not correct : should return an error
try:
    client = meteofranceClient("foo", True)
    print(client.get_data())
except meteofranceError as exp:
    print(exp)

#pointe-a-pitre : result from meteo-france is different and it returns less data
try:
    client = meteofranceClient(97110, True)
    print(client.get_data())
except meteofranceError as exp:
    print(exp)

try:
    client = meteofranceClient(80000, True)
    print(client.get_data())
except meteofranceError as exp:
    print(exp)

"""
#if needed, test update
print("waiting 5 minutes to show update")
time.sleep(300)
client.update()
print(client.get_data())
"""


print("DONE")
exit()
