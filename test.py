from meteofrance.client import meteofranceClient, meteofranceError
import time

try:
    client = meteofranceClient(13000)
    print(client.get_data())
except meteofranceError as exp:
    print(exp)

try:
    client = meteofranceClient(95750)
    print(client.get_data())
except meteofranceError as exp:
    print(exp)


"""
mf=meteofrance(13000)
print mf.get_data()

mf=meteofrance(76000)
print mf.get_data()

print "waiting 5 minutes to show update"
time.sleep(300)
mf.update()
print mf.get_data()
"""


print("DONE")
exit()
