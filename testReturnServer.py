import socket
import MySQLdb
from geopy.distance import vincenty
import time

HOST=''
PORT=8089
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((HOST,PORT))
s.listen(1)
conn, addr=s.accept()
print('Connected by',addr)

#db = MySQLdb.connect('localhost','root','0893','traccardb1')
#cursor = db.cursor()

while True:
    data=conn.recv(1024)
    if not data:
        break

    db = MySQLdb.connect('localhost','root','0893','traccardb1')
    cursorPositions = db.cursor()
    cursorLocations = db.cursor()    

    cursorPositions.execute("select * from (select deviceid,MAX(devicetime) as devicetime from positions group by deviceid) as A join (select deviceid,devicetime,latitude,longitude from positions) as B on A.deviceid = B.deviceid and A.devicetime = B.devicetime;")
    
    positionRows = cursorPositions.rowcount
    conn.send(str(positionRows))

    for j in xrange(positionRows):
        lastdata = cursorPositions.fetchone()
        usr_id = lastdata[2]
        usr_pos = (lastdata[4],lastdata[5])

        cursorLocations.execute("select * from locations")
    
        for i in xrange(cursorLocations.rowcount):
            place,loc_lati,loc_longi,scope,clock = cursorLocations.fetchone()
            loc_pos = (loc_lati,loc_longi)
            distance = vincenty(usr_pos,loc_pos).meters
            if i==0:
                nearest = (place,distance,distance<scope)
            elif(distance<nearest[1]):
                nearest = (place,distance,distance<scope)	

        msg = str(j+1)+" "+nearest[0]+" "+str(nearest[1])+" "+str(nearest[2])
        print(msg)
        conn.send(msg)
        isReceived = conn.recv(1024)
        print(isReceived)

    db.close()

conn.close()
