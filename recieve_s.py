import socket
import pyrebase
import datetime
"""
СОСТОЯНИЕ: 8.02.20 ГОТОВ

Программа получает данные по UDP и используя тип данных и мак(ищет присланный мак в бд) вносит их в бд. Если устройство не найдено,
данные игнорируются. Работает при наличии 1 в isActivated.
DC.0E.A1.4A.C5.DE#s_temp*0018
DC.0E.A1.4A.C5.DE#s_co2-*0500
"""

import time
import math

config = {
  "apiKey": "apiKey",
  "authDomain": "projectId.firebaseapp.com",
  "databaseURL": "https://smarthome-5b591.firebaseio.com/",
  "storageBucket": "projectId.appspot.com"
}

uid_file = '/home/pi/SmartHome/uid'
isActivated_file = '/home/pi/SmartHome/isActivated'
dbisUpdated_file = '/home/pi/SmartHome/dbisUpdated'
logEnabled_file = '/home/pi/SmartHome/logEnabled'

#activation check
with open(isActivated_file) as afile_handler:
	ActivationStatus = afile_handler.read(1)
	ActStatus = bool(int(ActivationStatus))
	
while(not ActStatus):
	time.sleep(5)
	with open(isActivated_file) as afile_handler:
		ActivationStatus = afile_handler.read(1)
		ActStatus = bool(int(ActivationStatus))

#log check
with open(logEnabled_file) as lfile_handler:
		LogStatus = lfile_handler.read(1)
		LStatus = bool(int(LogStatus))	
	
UDP_PORT_RECIEVE =1234 #1112
UDP_IP_RECIEVE = ""

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP recieve
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.settimeout(40)
s.bind((UDP_IP_RECIEVE, UDP_PORT_RECIEVE))

if LStatus:
	print(str(datetime.datetime.now()))
	print("Socket opened on port 1112")

with open(uid_file) as file_handler:
	uid = file_handler.read().splitlines()

m="68:c6:3a:ab:57:2a"

firebase = pyrebase.initialize_app(config)
with open(dbisUpdated_file, "w") as pfile_handler:
				pfile_handler.write("1")

#for room in db.get().keys():
#	print(room.key())
#	for d in db.child(room.key()).get().each():
#		print(d)
	#	if d == m:
	#		print(room.val())
if LStatus:
	print("firebase init ok. Start listening..")
while(True):
	try:
		data, addr = s.recvfrom(256)
		with open(dbisUpdated_file) as гfile_handler:
			UpdStatus = гfile_handler.read(1)
			UStatus = bool(int(UpdStatus))
		if UStatus == True:
			b = firebase.database().child("users").child(uid[0])
			db = b.get()
			with open(dbisUpdated_file, "w") as ufile_handler:
				ufile_handler.write("0")
		try:
			d = data.decode().split('#')
			mac = d[0]
			device = d[1].split("*")[0]
			val = d[1].split("*")[1]
			
			device_only = device[1:] #_c02
			m_device_only = "m" + device_only
			deviceToWrite = "s" + device_only + "_"
		except IndexError:
			print("parsing error")
		if LStatus:
			print(str(datetime.datetime.now()))
			print("Recieved: ",mac,device_only,val)
		for user in db.each():
			#print(user.key()) #room
			for d in user.val().items(): #all under room folder
				#print(d)
				if d[0].find(m_device_only) != -1:
					print("Found in db: " + d[0])
					N = d[0][7]
					#print(N)
					mac_fb = d[1]
					if mac_fb == mac:
						deviceToWrite += N
						b.child("users").child(uid[0]).child(user.key()).update({deviceToWrite: val})
						time.sleep(10)
				#b.child("users").child(uid[0]).child(user.key()).update({deviceToWrite: val})
		print("")
	except socket.timeout:
		#print("TIMEOUT")
		pass
