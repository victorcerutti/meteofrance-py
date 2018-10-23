from meteofrance import meteofrance

mf=meteofrance(95142)
data = mf.get_data()

print data

mf.update()
print data

print "DONE"
