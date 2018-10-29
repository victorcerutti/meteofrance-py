from meteofrance.client import meteofranceClient, meteofranceError
import time

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

#pointe-à-pitre : result from météo-france is different and it returns less data
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
