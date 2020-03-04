"""
читает файл task1 и управляет d при наступлении условия,
записанном в файле

todo: отправка уведомлений + протестировать всё
"""
import time
import pyrebase
import datetime
import os
import udp_send


uid_file = '/home/pi/SmartHome/uid'
task_file = '/home/pi/SmartHome/Tasks/task2'

isActivated_file = '/home/pi/SmartHome/isActivated'

config = {
  "apiKey": "apiKey",
  "authDomain": "projectId.firebaseapp.com",
  "databaseURL": "https://smarthome-5b591.firebaseio.com/",
  "storageBucket": "projectId.appspot.com"
}

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

firebase = pyrebase.initialize_app(config)
db = firebase.database()

def compare(a, b, comp):
	if comp == "<":
		if a < b:
			return True
		else:
			return False
	elif comp == ">":
		if a > b:
			return True
		else:
			return False

def log(s):
	print(str(datetime.datetime.now()) ,  s)
		
def stream_handler(message):
	path = message["path"]
	if path == '/':
		print(str(datetime.datetime.now()) + ' Connected to database')
	elif path.find("s") == -1:
		print(str(datetime.datetime.now()) + 'no s error')
	else:
		print(message["path"])
		
		if os.path.exists(task_file):
			try:
				with open(task_file, "r") as f:
					mac_s = f.readline().rstrip('\n')
					comp = f.readline().rstrip('\n')
					val_fromfile = f.readline().rstrip('\n')
					action = f.readline().rstrip('\n')
					if action.isnumeric():
						mac_d = f.readline().rstrip('\n')
			except IOError:
				log("file open error")
				
			print(mac_s)
			print(comp)
			print(val_fromfile)
			print(action)
		
			s_path = path.split('/')
			room = s_path[1]
			device = s_path[2]
			macword = 'm' + device[1:]
			db1 = db.child("users").child(uid[0]).child(room).child(macword).get()
			val = db.child("users").child(uid[0]).child(room).child(device).get()
			value = val.val()
			mac = db1.val()
			print(str(datetime.datetime.now()))
			print("MAC of device: {}".format(mac))
			print("Device: {}".format(device))
			print("Action: {}".format(value))
		
			if action == "n":
				pass
				#send notification to android
			else:
				if mac_s == mac and compare(value, val_fromfile, comp):
					msg = mac_d + "#d*" + action
					udp_send.send(msg)
					print("sent")
					time.sleep(20)
		else:
			log("no file")
			
			
my_stream = db.child("users").child(uid[0]).stream(stream_handler)
	
