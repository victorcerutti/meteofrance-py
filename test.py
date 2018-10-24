from meteofrance import meteofrance
import time

mf=meteofrance(13000)
print mf.get_data()

mf=meteofrance(76000)
print mf.get_data()

print "waiting 5 minutes to show update"
time.sleep(300)
mf.update()
print mf.get_data()

print "DONE"
