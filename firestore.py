"""
СОСТОЯНИЕ: 8.02.20 ГОТОВ

работает с firestore и отвечает за поддержку истории показаний устройств

автоматически сдвигяются на час предыдущие показания во всех комнатах
названия комнат в firestore соответствуют первичным названиям в firebase
в нулевой час записываются текущие показания
Записи в firestore создаются при добавлении комнаты
# - разделитель
* - показания
Пример: s_temp_0*24#s_co2-_0*550
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

import firebase_admin
import google.cloud
import pyrebase
from firebase_admin import credentials, firestore
import time
import datetime

uid_file = '/home/pi/SmartHome/uid'
isActivated_file = '/home/pi/SmartHome/isActivated'
logEnabled_file = '/home/pi/SmartHome/logEnabled'

config = {
  "apiKey": "apiKey",
  "authDomain": "projectId.firebaseapp.com",
  "databaseURL": "https://smarthome-5b591.firebaseio.com/",
  "storageBucket": "projectId.appspot.com"
}

scheduler = BackgroundScheduler()
scheduler.start() 

firebase = pyrebase.initialize_app(config)

#activation check
with open(isActivated_file) as afile_handler:
	ActivationStatus = afile_handler.read(1)
	ActStatus = bool(int(ActivationStatus))
	
while(not ActStatus):
	time.sleep(5)
	with open(isActivated_file) as afile_handler:
		ActivationStatus = afile_handler.read(1)
		ActStatus = bool(int(ActivationStatus))

with open(uid_file) as file_handler:
	uid = file_handler.read().splitlines()

#log check
with open(logEnabled_file) as lfile_handler:
	LogStatus = lfile_handler.read(1)
	LStatus = bool(int(LogStatus))	

cred = credentials.Certificate("/home/pi/firebase_key.json")
app = firebase_admin.initialize_app(cred)

db = firestore.client()
doc_ref = db.collection(u'uid').document(u'библиотека')
doc_ref.set({
    u'7': u's_temp_0*24#s_co2-_0*550',
	u'6': u's_temp_0*23#s_co2-_0*612',
	u'5': u's_temp_0*20#s_co2-_0*1249',
	u'4': u'',
	u'3': u'',
	u'2': u'',
	u'1': u's_temp_0*20#s_co2-_0*1249',
	u'0': u'',
})

doc_ref = db.collection(u'uid').document(u'чердак')
doc_ref.set({
    u'7': u's_temp_0*24',
	u'6': u's_temp_0*23',
	u'5': u's_temp_0*20',
	u'4': u'',
	u'3': u'',
	u'2': u'',
	u'1': u'',
	u'0': u'',
})
if LStatus:
	print(str(datetime.datetime.now()) + "Started")
	print("Current uid: ",uid[0])

def upd_firestore():
	b = firebase.database().child("users").child(uid[0])
	db = b.get()
	room_names = []
	N = [] #number of sensors in room
	values = []
	Strings_to_write = {}
	i = 0
	for user in db.each():
		N.append(0)
		#print(user.key())# room
		if user.key() != "FCM_id":
			Strings_to_write[user.key()] = ""
			String_to_write = ""
			for d in user.val().items(): #all under room folder
				if d[0].find("s_") != -1:
					N[i] += 1
					String_to_write += "#"
					String_to_write += d[0] #example s_temp_0
					String_to_write += "*"
					String_to_write += str(d[1])
			Strings_to_write[user.key()] = String_to_write	
		i+=1
	if LStatus:
		print(str(datetime.datetime.now()) + " Updating firestore")				
		print(Strings_to_write)
	
	Dict = {}

	db = firestore.client()
	users_ref = db.collection(u'uid')
	docs = users_ref.stream()

	for doc in docs:
		##print(u'{} => {}'.format(doc.id, doc.to_dict()))
		#print(doc.id)
		dic = doc.to_dict()
		for key in dic:
			if key == "0":
				Dict["1"] = dic[key]
				#Dict["0"] = "new"
				try:
					Dict["0"] = Strings_to_write[doc.id]
				except KeyError:
					Dict["0"] = ""
					print("Mismatching data ERROR!")
				#print(0,"old->",dic[str(0)])
				#print(1,"old->",dic[str(1)])
				#print(0,"new->",Dict[str(0)])
				#print(1,"new->",Dict[str(1)])
			elif key == "7":
				#print("7")
				pass
			else:
				new_key = str(int(key)+1)
				Dict[new_key] = dic[key]
				#print(new_key,"new->",Dict[new_key])
				#print(new_key,"->",Dict[new_key])
		#print(doc.id) #room name current
		db.collection(u'uid').document(doc.id).set(Dict)
	
scheduler.add_job(upd_firestore, 'interval', minutes=1, id='upd_firestore',  replace_existing=True)

while 1:
    time.sleep(10)
