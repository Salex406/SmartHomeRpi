"""
СОСТОЯНИЕ: 25.02.20 ПРОТЕСТИТЬ

Программа мониторит изменения в бд для устройств d. При изменении(вкл или выкл)
вызывается программа отправки команды по UDP, затем делается запись 3 в соответствующий d

Формат:
DC:0E:A1:4A:C5:DE#d*1
"""

import pyrebase
import time
import datetime
import socket

UDP_IP = "255.255.255.255"
UDP_PORT = 1113

config = {
  "apiKey": "apiKey",
  "authDomain": "projectId.firebaseapp.com",
  "databaseURL": "https://smarthome-5b591.firebaseio.com/",
  "storageBucket": "projectId.appspot.com"
}

uid_file = '/home/pi/SmartHome/uid'
isActivated_file = '/home/pi/SmartHome/isActivated'
logEnabled_file = '/home/pi/SmartHome/logEnabled'

#activation check
with open(isActivated_file) as afile_handler:
	ActivationStatus = afile_handler.read(1)
	ActStatus = bool(int(ActivationStatus))
	
while(not ActStatus):
	time.sleep(10)
	with open(isActivated_file) as afile_handler:
		ActivationStatus = afile_handler.read(1)
		ActStatus = bool(int(ActivationStatus))
		
#log check
with open(logEnabled_file) as lfile_handler:
		LogStatus = lfile_handler.read(1)
		LStatus = bool(int(LogStatus))
	
#read uid
with open(uid_file) as file_handler:
	uid = file_handler.read().splitlines()
	#print(uid[0])
	
firebase = pyrebase.initialize_app(config)
db = firebase.database()


"""
Система наименований:
s - сенсор
d - выполняет действие
m - уникальный мак или адрес в случае nrf
n - отображаемое пользовательское имя (проект)


empty - для пустой комнаты. игнорируется приложением
в конце следует номер устройства. нумерация  с нуля
прочерк - ненужное место для символа

s_temp_0
m_temp_0
пара создается при добавлении устройства
Примеры
s_co2-_1
s_watr_

"""

	
def stream_handler(message):
	#print(message["event"]) # put
	#print(message["data"])
	path = message["path"]
	if path == '/':
		#one time for each launch
		if LStatus:
			print(str(datetime.datetime.now()) +' Connected to database')
	elif path.find("d") == -1:
		if LStatus:
			print(str(datetime.datetime.now()) +'no d error')
	else:
		#print(message["event"])
		print(message["path"])
		
		s_path = path.split('/')
		room = s_path[1]
		device = s_path[2]
		#print(room)
		print(device)
		#print(message["data"])
		
		#only
		if device[0] == 'd':
			#find mac of the device
			macword = 'm' + device[1:]
			#print(macword)
			db1 = db.child("users").child(uid[0]).child(room).child(macword).get()
			val = db.child("users").child(uid[0]).child(room).child(device).get()
			mac = db1.val()
			value = val.val()
			if LStatus:
				print(str(datetime.datetime.now()))
				print("MAC of device: " ,mac)
				print("Device: " + device)
				print("Action: " + str(value))
			
			msg = mac + "#d*" + str(value)
			Zval = 3
			b = firebase.database().child("users").child(uid[0])
			b.child(room).update({device: Zval})
			#print(msg)
			try:
				sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))
			except socket.timeout:
				if LStatus:
					print(str(datetime.datetime.now()) + " Socket timeout error")
				pass
			except socket.error:
				if LStatus:
					print(str(datetime.datetime.now()) + " Socket error")
				pass
my_stream = db.child("users").child(uid[0]).stream(stream_handler)

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
