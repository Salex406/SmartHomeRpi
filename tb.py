import sys
import time
import telepot
import subprocess
from subprocess import Popen, PIPE, run
import os
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.blocking import BlockingScheduler
from time import sleep
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
scheduler.start()  

telepot.api.set_proxy('http://127.0.0.1:8118')

temp=0.0
hum=0.0
lux=0
co2=0

file_read_outlet = '/home/pi/outlet_state_rq.py'
file_on_outlet = '/home/pi/outlet_on.py'
file_off_outlet = '/home/pi/outlet_off.py'

temper_id = "/home/pi/alert_state/t_on"
motion_id = "/home/pi/alert_state/m_on"
min_temp = "/home/pi/alert_state/min_temp"
max_temp = "/home/pi/alert_state/max_temp"
temp_action = "/home/pi/alert_state/action_temp"

id_write_min_temper = 0
id_write_max_temper = 0

def rq_climate(): 
	global temp
	global hum
	global lux
	global co2
	with open('/home/pi/environment/bin/c.txt') as f:
		temp, hum, lux, co2= [float(x) for x in next(f).split()] 
		#print(w)
		#print(h)
		f.close()

def print_co2():
	global co2
	chat_id = 725739430  #telegram id
	#print (co2)
	bot.sendMessage(chat_id, 'CO2, ppm: %s' %co2)

def alert_info_f(file_id):
	if os.path.exists(file_id):
		text = "Сигнализация сейчас активна"
	else:
		text = "Сигнализация сейчас отключена"
	return text

def outlet_read():
	#r = subprocess.call(['python3.6', file_read_outlet])
	
	command = ['python3.6', file_read_outlet]
	result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
	#print(result.returncode, result.stdout, result.stderr)
	#print(type(result.stdout))
	if int(result.stdout) == 1:
		r='Розетка включена.'
	elif int(result.stdout) ==0:
		r='Розетка выключена.'
	else: 
		r='Ошибка!'
	return r

def outlet_on():
	command = ['python3.6', file_on_outlet]
	result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
	
def outlet_off():
	command = ['python3.6', file_off_outlet]
	result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)

def alert_f(alarm, file_id):
	#сигнализация уже включена
	if alarm == 'on' and os.path.exists(file_id):
		text = "Сигнализация уже была включена"
	#была включена, теперь отключаем
	elif alarm == 'off' and os.path.exists(file_id):
		text = "Отключаю сигнализацию"
		subprocess.call("rm -f %s" %file_id, shell=True)
	#уже была выключена, выключать не надо
	elif alarm == 'off' and os.path.exists(file_id) == False:
		text = "Сигнализация уже была отключена"
	#выла выключена, теперь включаем
	elif  alarm == 'on' and os.path.exists(file_id) == False:	
		text = "Активирую сигнализацию"
		subprocess.call("touch %s" %file_id, shell=True)
	else:
		text = "err"
	return text

def c_t_read():
	proc = Popen(['cat %s' %min_temp], shell=True, stdout=PIPE, stderr=PIPE)
	proc.wait()
	c_t = proc.communicate()[0]
	c_t = c_t.decode(encoding='utf-8')
	#procm = Popen(['cat %s' %max_temp], shell=True, stdout=PIPE, stderr=PIPE)
	#procm.wait()
	#t = procm.communicate()[0]
	#t = c.decode(encoding='utf-8')
	c_t = "\nПорог срабатывания по минимуму установлен на "+c_t+" градусов"
	#t = "\nПорог срабатывания по максимуму установлен на "+t+" градусов"
	return c_t

def on_chat_message(msg):
	global id_write_min_temper
	#global id_write_max_temper
	content_type, chat_type, chat_id = telepot.glance(msg)
	command = msg['text'].lower()
	print(command)
	if command == '/start':
		markup = ReplyKeyboardMarkup(keyboard=[[dict(text='Статус')],[dict(text='Прямое управление')],[dict(text='Планировщик')],[dict(text='Сигнализация')]])
		bot.sendMessage(chat_id, 'Привет! Выбери опцию.', reply_markup=markup)
  #  keyboard = InlineKeyboardMarkup(inline_keyboard=[
  #                 [InlineKeyboardButton(text='Press me', callback_data='press')],
  #             ])
	#keyboard = ReplyKeyboardMarkup(keyboard=[['Add', 'List'], ['Settings', 'Web'], ["Персик","Лив"]])
	#bot.sendMessage(chat_id, 'Use inline keyboard', reply_markup=keyboard)

	elif command == 'главное меню':
			markup = ReplyKeyboardMarkup(keyboard=[[dict(text='Статус')],[dict(text='Прямое управление')],[dict(text='Планировщик')],[dict(text='Сигнализация')]])
			bot.sendMessage(chat_id, 'Выберите опцию.', reply_markup=markup)
			
	elif command == 'статус':
			markup = ReplyKeyboardMarkup(keyboard=[[dict(text='Статус')],[dict(text='Прямое управление')],[dict(text='Планировщик')],[dict(text='Сигнализация')]])
			global temp
			global hum
			global lux
			global co2
			bot.sendMessage(chat_id, 'Текущая освещённость: %s люкс.' %lux)
			bot.sendMessage(chat_id, 'Текущая температура: %s' %temp)
			bot.sendMessage(chat_id, 'Текущая влажность: %s' %hum)
			bot.sendMessage(chat_id, 'CO2, ppm: %s' %co2, reply_markup=markup)
			
	#elif command == 'климат': #вернулись в главное меню
	#		markup = ReplyKeyboardMarkup(keyboard=[[dict(text='Статус')],[dict(text='Прямое управление')],[dict(text='Планировщик')],[dict(text='Сигнализация')]])
	#		global temp
	#		global hum
	#		global lux
	#		global co2
	#		bot.sendMessage(chat_id, 'Текущая освещённость: %s люкс.' %lux)
	#		bot.sendMessage(chat_id, 'Текущая температура: %s' %temp)
	#		bot.sendMessage(chat_id, 'Текущая влажность: %s' %hum)
	#		bot.sendMessage(chat_id, 'CO2, ppm: %s' %co2, reply_markup=markup)
	
	elif command == 'планировщик':
			#c = '\U0001F61C'
			markup = ReplyKeyboardMarkup(keyboard=[[dict(text='По температуре')], [dict(text='Главное меню')]])
			bot.sendMessage(chat_id, "Выбери опцию.", reply_markup=markup)
	
	elif command == 'управление':
			markup = ReplyKeyboardMarkup(keyboard=[[dict(text='Розетка')],[dict(text='Главное меню')]])
			bot.sendMessage(chat_id, 'Выбери опцию.', reply_markup=markup)
	
	elif command == 'розетка':
			markup = InlineKeyboardMarkup(inline_keyboard=[
			[dict(text='Включить', callback_data='outlet_on'), dict(text='Отключить', callback_data='outlet_off')],
			[dict(text='Текущее состояние', callback_data='outlet_info')],
			])
			message_with_inline_keyboard = bot.sendMessage(chat_id, 'Опции для розетки:', reply_markup=markup)
			
	elif command == 'при повышении':
			comm='1'
			subprocess.call("echo %s > %s" %(comm, temp_action), shell=True)
			markup = ReplyKeyboardMarkup(keyboard=[[dict(text='Главное меню')]])
			message_with_inline_keyboard = bot.sendMessage(chat_id, 'Действие будет выполнено при превышении порога. Нажми кнопку для возврата в главное меню.', reply_markup=markup)
	
	elif command == 'при понижении':
			comm='0'
			subprocess.call("echo %s > %s" %(comm, temp_action), shell=True)
			markup = ReplyKeyboardMarkup(keyboard=[[dict(text='Главное меню')]])
			message_with_inline_keyboard = bot.sendMessage(chat_id, 'Действие будет выполнено при температуре ниже порога. Нажми кнопку для возврата в главное меню.', reply_markup=markup)	

	elif command == 'по температуре':
			markup = InlineKeyboardMarkup(inline_keyboard=[
			[dict(text='Включить', callback_data='temp_on'), dict(text='Отключить', callback_data='temp_off')],
			[dict(text='Порог срабатывания', callback_data='temp_alert_min')],
			[dict(text='Текущее состояние', callback_data='temp_alert_info')],
			])
			message_with_inline_keyboard = bot.sendMessage(chat_id, 'Опции сигнализации температуры:', reply_markup=markup)
	
	elif command == 'сигнализация':
			markup = ReplyKeyboardMarkup(keyboard=[
			[dict(text='Протечка')],
			[dict(text='Контроль движения')],
			[dict(text='Главное меню')],
			])
			bot.sendMessage(chat_id, 'Какой раздел необходим?', reply_markup=markup)
			
	elif command == 'контроль движения':
			markup = InlineKeyboardMarkup(inline_keyboard=[
			[dict(text='Включить', callback_data='motion_on'), dict(text='Отключить', callback_data='motion_off')],
			[dict(text='Состояние', callback_data='motion_alert_info')]])
			message_with_inline_keyboard = bot.sendMessage(chat_id, 'Опции сигнализации движения:', reply_markup=markup)
			
	else:
			if id_write_min_temper == 1:
				#если происходит установка температуры срабатывания
				if command.isdigit():
					subprocess.call("echo %s > %s" %(command, min_temp), shell=True)
					c = '\U00002705'
					bot.sendMessage(chat_id, str("Температурный порог установлен в %s градусов ") %command + c)
					markup = ReplyKeyboardMarkup(keyboard=[[dict(text='При повышении')], [dict(text='При понижении')]])
					bot.sendMessage(chat_id, 'Действие надо выпонлять при повышении температуры выше порога или понижении:' , reply_markup=markup)
					
					id_write_min_temper = 0
				else:
					markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Главное меню')]])
					bot.sendMessage(chat_id, str("%s - это не целое число. При необходимости пройдите настройку заново. Значение не установлено!") %command, reply_markup=markup)
					id_write_min_temper = 0		
def on_callback_query(msg):#когда нажимаем на Inline
	query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
	print('Callback Query:', query_id, from_id, data)
	global id_write_min_temper
	global id_write_max_temper
	if data == 'outlet_on':
		outlet_on()
		bot.answerCallbackQuery(query_id, text='Розетка включена' , show_alert=True)
	elif data == 'outlet_off':
		outlet_off()
		bot.answerCallbackQuery(query_id, text='Розетка выключена' , show_alert=True)
	elif data == 'outlet_info':
		R=str(outlet_read())
		bot.answerCallbackQuery(query_id, text='%s'%R, show_alert=True)
    #bot.answerCallbackQuery(query_id, text='Got it')

	elif data == 'temp_on':
			inf = str(alert_f('on', temper_id))
			bot.answerCallbackQuery(query_id, text='%s' %inf, show_alert=True)
	elif data == 'temp_off':
			inf = str(alert_f('off', temper_id))
			bot.answerCallbackQuery(query_id, text='%s' %inf, show_alert=True)
	elif data == 'temp_alert_info':
			inf = str(alert_info_f(temper_id))
			#info_c_t = str(c_t_read())
			#inf = inf+info_c_t
			bot.answerCallbackQuery(query_id, text='%s' %inf, show_alert=True)
	elif data == 'temp_alert_min':
			id_write_min_temper = 1
			bot.answerCallbackQuery(query_id, text='Установите порог температуры. Введите целое число.', show_alert=True)
			
	elif data == 'motion_on':
			inf = str(alert_f('on', motion_id))
			bot.answerCallbackQuery(query_id, text='%s' %inf, show_alert=True)
	elif data == 'motion_off':
			inf = str(alert_f('off', motion_id))
			bot.answerCallbackQuery(query_id, text='%s' %inf, show_alert=True)
	elif data == 'motion_alert_info':
			inf = str(alert_info_f(motion_id))
			bot.answerCallbackQuery(query_id, text='%s' %inf, show_alert=True)

#	elif data == 'temp_alert_max':
#			id_write_max_temper = 1
#			bot.answerCallbackQuery(query_id, text='Установите максимальный порог температуры. Введите целое число.', show_alert=True)
	
bot = telepot.Bot('723878232:AAGdicggv2sGpZ5EZnRbmNZHd0Uvy_rS89o')
MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()
print('Listening ...')
scheduler.add_job(rq_climate, 'interval', seconds=30, id='rq_climate',  replace_existing=True)

scheduler.add_job(print_co2, 'interval', minutes=15, id='print_co2',  replace_existing=True)

while 1:
    time.sleep(10)
