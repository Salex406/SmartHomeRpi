"""
Принимает предопределенный тревожный сигнал ("alrm" и т.д),
атем отправляет уведомление на устройство, на котором появляется уведомление
или активность, привлекающие внимание польователя.
fcm_id читается при запуске из файла
активация по isActivated
"""


from pyfcm import FCMNotification
import time
import pyrebase

uid_file = '/home/pi/SmartHome/uid'
fcm_id_file = '/home/pi/SmartHome/fcm_id'
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
	time.sleep(10)
	with open(isActivated_file) as afile_handler:
		ActivationStatus = afile_handler.read(1)
		ActStatus = bool(int(ActivationStatus))

#read uid
"""
with open(uid_file) as file_handler:
	uid = file_handler.read().splitlines()
	#print(uid[0])
uid вроде пока не нужен. нужен лишь fcm id
"""

"""
registration_id = 0
with open(fcm_id_file) as file_handler:
	registration_id = file_handler.read().splitlines()
	print(registration_id)
"""
firebase = pyrebase.initialize_app(config)
db = firebase.database()

#api key is same for all project
#reg id from database
api_key = "AAAA_0amNdA:APA91bHySFa8_t-oT508TknNpmwrT8HkrC8hrRgq_N4HkbszSx0EiH9n-3EdK0KWriNnRJOF64gVcSu4YHJdotU5zl1r-ImfrAgOCpiczQDeonPqFwh2TWzP4fevTh_9n7_ayLPbRHla"
registration_id = "eHtVtpM6RkU:APA91bFrxywbXzQxenwm91ZCqeCCmmaqoqZI8FZERYpMRBqUJ8thHzKrVGraOAWMLF_zMw-WIfCBWNnfhbRHRAlTC0uN9BtIJPqzmkgSaUWBGPGlx1ujGgUbuTrf4ng5xS54FBOZP01P"

push_service = FCMNotification(api_key)

data_message = {
    "Nick" : "Mario",
    "body" : "great match!",
    "Room" : "PortugalVSDenmark"
}
#show activity on top of screen from service

#registration_id = "f-p1fW2m2vg:APA91bE0PLBR7DrYZnO3RwruhJu2Mij5b_ggqpLq6Aw6Z0Mb8zUKVuIk0fAjPxw-GcZx7lhIP9yNDFf5QfOG1p74G6bxoRH9WApbiApYyIwW7Pn-9CB7uBnyBboSkRA54j56fdfdOqF2"
message_title = "ппо141"
message_body = "Текст сообщения"
result = push_service.single_device_data_message(registration_id=registration_id, data_message=data_message)
#result = push_service.notify_single_device(registration_id=registration_id, message_body=message_body, data_message=data_message)
print(result)

