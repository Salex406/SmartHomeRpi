"""
Мониторит изменения в firestore/uid/t1
при получении изменений переписывает task1.txt - по условию
task_t1 - по времени

todo:
реализовать случай t
"""

import subprocess
import time
import datetime
import firebase_admin
import google.cloud
import pyrebase
from firebase_admin import credentials, firestore

uid_file = '/home/pi/SmartHome/uid'
isActivated_file = '/home/pi/SmartHome/isActivated'
logEnabled_file = '/home/pi/SmartHome/logEnabled'

task_t_file = '/home/pi/SmartHome/Tasks/task_t1'
task_file = '/home/pi/SmartHome/Tasks/task2'

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

config = {
  "apiKey": "apiKey",
  "authDomain": "projectId.firebaseapp.com",
  "databaseURL": "https://smarthome-5b591.firebaseio.com/",
  "storageBucket": "projectId.appspot.com"
}

firebase = pyrebase.initialize_app(config)
cred = credentials.Certificate("/home/pi/firebase_key.json")
app = firebase_admin.initialize_app(cred)

db = firestore.client()

#p = subprocess.Popen(['python3', 'task1.py'])
# continue with your code then terminate the child
#time.sleep(10)
#p.terminate()

def log(s):
	if LStatus:
		print(str(datetime.datetime.now()) ,  s)

def decode(stri):
	if stri[1] == "s":
		log("Detected sensor case")
		s_dev = stri[3:11]
		mac = stri[12:29]
		comparation = stri[30]
		start_val = 32
		stop_val = stri.find("*", 32)
		val = stri[32:stop_val]
		if stri.find("n") != -1:
			log("notify")
			log(s_dev)
			log(mac)
			log(comparation)
			log(val)
			with open(task_file, "w") as f:
				f.write(mac + "\n")
				f.write(comparation + "\n")
				f.write(val + "\n")
				f.write("n")
			
			#notify
		else:
			log("use device")
			log(s_dev)
			log(mac)
			log(comparation)
			log(val)
			d_dev = stri[stop_val+1:stop_val+9]
			mac_dev = stri[stop_val+10:stop_val+27]
			action = stri[stop_val+28]
			log(d_dev)
			log(mac_dev)
			log(action)
			with open(task_file, "w") as f:
				f.write(mac + "\n")
				f.write(comparation + "\n")
				f.write(val + "\n")
				f.write(action + "\n")
				f.write(mac_dev)
			pass
	elif stri[1] == "t":
		log("Detected timing case")
		start_val = 3
		stop_val = stri.find("*", start_val)
		hour = stri[start_val:stop_val]
		
		start_val = stop_val + 1
		stop_val = stri.find("*", start_val)
		minute = stri[start_val:stop_val]
		log(hour)
		log(minute)
		start_val = stri.find("*", stop_val + 1)
		stop_val = stri.find("*", start_val + 1)
		mac = stri[start_val + 1:stop_val]
		action = stri[stop_val + 1]
		log(mac)
		log(action)
		with open(task_t_file, "w") as f:
				f.write(mac + "\n")
				f.write(comparation + "\n")
				f.write(val + "\n")
				f.write("n")
	else:
		log("Task is incorrect")
		

# Create a callback on_snapshot function to capture changes
def on_snapshot(doc_snapshot, changes, read_time):
	for doc in doc_snapshot:
		if LStatus:
			print(str(datetime.datetime.now()) +  u' Received document snapshot: {}'.format(doc.id))
		dic = doc.to_dict()
		for key in dic:
			print(dic[key])
			if dic[key][0] == "#":
				decode(dic[key])
			elif LStatus:
				print(str(datetime.datetime.now()) + " String is incorrect")
			
			#terminate,write new and launch

doc_ref = db.collection(u'uid').document(u't1')

# Watch the document
doc_watch = doc_ref.on_snapshot(on_snapshot)

if LStatus:
	print(str(datetime.datetime.now()) + " Start listening")
	
while True:
	time.sleep(2)
