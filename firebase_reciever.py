"""
Программа мониторит изменения в бд для устройств d. При изменении(вкл или выкл)
вызывается программа отправки команды по UDP, затем делается запись в соответствующий s
"""

import pyrebase
import time
import datetime

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
#allk = db.child("users").child(uid[0]).child('кухня').child('s_temp_0').get()
#for sth in allk.each():
#	print(sth.key())
#	print(sth.val())

#print(allk.key())
#print(allk.val())
	
def stream_handler(message):
	#print(message["event"]) # put
	#print(message["data"])
	path = message["path"]
	if path == '/':
		#one time for each launch
		if LStatus:
			print(str(datetime.datetime.now()) +' Connected to database')
	else:
		#print(message["event"])
		#print(message["path"])
		
		s_path = path.split('/')
		room = s_path[1]
		device = s_path[2]
		#print(room)
		#print(device)
		#print(message["data"])
		
		#only
		if device[0] == 'd':
			#find mac of the device
			macword = 'm' + device[1:]
			#print(macword)
			db1 = db.child("users").child(uid[0]).child(room).child(macword).get()
			mac = db1.val()
			#print("MAC of device: " ,mac)
			
			#ПЛАН вызов функции отправки широковещ удп. Фильтр мак на конечных устройствах
			#возврат записи бд в третье состояние
		
		#print(len(device)) 8 for all d-s
		
    #print(message["data"]["QcGrz5YYZbSZRKBNP6U1xXy4l9q2"].keys()) # {'title': 'Pyrebase', "body": "etc..."}
	#for room in message["data"].keys():
	#	print("room:",room)
#		for room in message["data"][uid].keys():
#			print("--", room)
#			for dev in message["data"][uid][room].keys():
#				print("---", dev)

#my_stream = db.child("users").child(uid[0]).stream(stream_handler)
my_stream = db.child("users").child(uid[0]).stream(stream_handler)
