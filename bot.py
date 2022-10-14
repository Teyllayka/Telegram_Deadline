import sqlite3
import telebot 
from telebot import types
from datetime import date, timedelta
from dateutil.parser import parse
import threading
from time import sleep
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


bot = telebot.TeleBot("//")

conn = sqlite3.connect('telegram.db', check_same_thread=False)
cursor = conn.cursor()
delay = 1800

user_dict = {}

class User:
    def __init__(self, name):
        self.id = id
        self.event = None
        self.date = None

ids = []		  



print(ids)


def db_table_val(id: int, userName: str):
	cursor.execute('INSERT INTO USERS (ID, USERNAME) VALUES (?, ?)', (id, userName))
	conn.commit()

def db_table_data(ID: int, EVENT: str, DATE: str):
	cursor.execute('INSERT INTO DATA (ID, EVENT, DATE) VALUES (?, ?, ?)', (ID, EVENT, DATE))
	conn.commit()


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
	
	result, key, step = DetailedTelegramCalendar().process(c.data)
	if not result and key:
		bot.edit_message_text("Когда вам напомнить?",
		c.message.chat.id,
		c.message.message_id,
		reply_markup=key)
	elif result:	
		if result >= date.today():
			user = user_dict[c.message.chat.id]	
			user.date = result
			db_table_data(c.message.chat.id, user.event, (user.date))
			bot.edit_message_text("Готово!", c.message.chat.id, c.message.message_id)
		else:
			bot.edit_message_text("Неправильная дата!", c.message.chat.id, c.message.message_id)
			sleep(1.5)
			calendar = DetailedTelegramCalendar().build()
			bot.edit_message_text("Когда вам напомнить?", c.message.chat.id, c.message.message_id,  reply_markup=calendar)
			#bot.send_message(c.message.chat.id, "Когда вам напомнить?", reply_markup=calendar)
		
		


@bot.message_handler(commands=['start'])
def start_message(message):	
	keyboard = types.InlineKeyboardMarkup()
	callback_button = types.InlineKeyboardButton(text="Автор", url="https://t.me/qeazxsw")
	callback_button2 = types.InlineKeyboardButton(text="Поддержать", url="https://www.donationalerts.com/r/Teyllay")
	keyboard.add(callback_button, callback_button2)



	cursor = conn.execute("SELECT COUNT(*) from USERS WHERE id = ?", (message.from_user.id,))
	row = cursor.fetchone()


	bot.send_message(message.chat.id, 'Привет! С помощью этого бота вы может поставить себе напоминатель для важный событий (/add)  чтобы начать', reply_markup=keyboard)




	if row[0] > 0:
			print("вы уже в базе данных") #bot.send_message(message.chat.id, 'вы уже в базе данных')
	else:
			us_id = message.from_user.id
			us_name = message.from_user.username
			
			db_table_val(id=us_id, userName=us_name)
			print("Ваше имя добавлено в базу данных!") #bot.send_message(message.chat.id, 'Ваше имя добавлено в базу данных!')
	

@bot.message_handler(commands=['help'])
def start_message(message):	
	bot.send_message(message.chat.id, '/add добавить событие')
	bot.send_message(message.chat.id, '/delete удалить событие')
	bot.send_message(message.chat.id, '/check проверить ближайшее событие')
	bot.send_message(message.chat.id, '/start чтобы начать пользоваться')


@bot.message_handler(commands=['add'])
def start_message(message):	
	msg = bot.reply_to(message, """ О чём вам напомнить? """)
	bot.register_next_step_handler(msg, process_name_step)

def process_name_step(message):
	chat_id = message.chat.id
	event = message.text
	user = User(chat_id)
	user.event = event
	user_dict[chat_id] = user
	calendar = DetailedTelegramCalendar().build()
	bot.send_message(message.chat.id,
                     "Когда вам напомнить?",
                     reply_markup=calendar)
	

CLICKED_BY = []	





@bot.message_handler(commands=['check'])
def start_message(message):	
		cursor = conn.execute("SELECT * from DATA WHERE id = ? ORDER BY DATE ", (message.from_user.id,))
		row = cursor.fetchone()

		if row != None:
			datee = date.today()
			datee = str(parse(row[2]).date() - datee )
			datee = datee[datee.find("1"):datee.rfind("d")]
			bot.send_message(message.chat.id, row[1])
			bot.send_message(message.chat.id, "Осталось " + datee + "дней")
		else:
			bot.send_message(message.chat.id, "У вас нету событий")

@bot.message_handler(commands=['delete'])
def start_message(message):	
		cursor = conn.execute("SELECT * from DATA WHERE id = ? ORDER BY DATE ", (message.from_user.id,))
		row = cursor.fetchall()
		row = list(row)
		i = 0
		if row != []:
			while i < len(row):
				bot.send_message(message.chat.id, row[i][1])
				i += 1
			msg = bot.send_message(message.chat.id,"выберите одно по номеру")
			bot.register_next_step_handler(msg, delete_step)	
		else:
			bot.send_message(message.chat.id, "У вас нету событий")

		
def delete_step(message):
	print("step")
	chat_id = message.chat.id
	num = message.text
	if num.isdigit():
		num = int(num)-1
		print("1")
		cursor = conn.execute("SELECT * from DATA WHERE id = ? ORDER BY DATE ", (chat_id,))
		row = cursor.fetchall()
		row = list(row)
		cursor = conn.execute("DELETE from DATA where id=? and EVENT=? ", (chat_id, row[num][1],))
		conn.commit()
		bot.send_message(chat_id, "Событие " + str(row[num][1]) + " Удалено")
	else:
		print("2")
		msg2 = bot.send_message(chat_id,"введите число")
		bot.register_next_step_handler(msg2, delete_step)


delete_conditions = []

def send_reminder():
	global ids


	
	while True:
		cursor = conn.execute("SELECT DISTINCT ID from DATA")
		row = cursor.fetchall()

		i = 0
		while i < len(row):
			id = str(row[i])
			id = id[id.find("(")+1:id.rfind(",")]
			ids.append(id)
			print(id)
			print(ids)
			i+=1
		for id in ids:
			cursor = conn.execute("SELECT COUNT(*) from DATA WHERE id = ?", (id,))
			row = cursor.fetchone()
			if row[0] > 0:
				cursor = conn.execute("SELECT * from DATA WHERE id = ? ORDER BY DATE ", (id,))
				row = cursor.fetchone()
				datee = date.today()		
				if row and (str(row[2]) == str(datee)) :
					bot.send_message(id, row[1])
					print(id, "(" + row[1] +") message sented")


					click_kb = types.InlineKeyboardMarkup()
					click_button = types.InlineKeyboardButton("CLICK HERE", callback_data='clicked')
					click_kb.row(click_button)
					bot.send_message(id, "<b>Вы увидели уведомление?</b>", parse_mode="HTML", reply_markup=click_kb, disable_web_page_preview=True)


					delete_conditions.append(id)
					delete_conditions.append(row[1])
					print(delete_conditions)

					
			
		sleep(delay) 


@bot.callback_query_handler(func=lambda call: call.data == 'clicked')
def command_click_inline(call):
	cid = call.message.chat.id
	uid = call.from_user.id
	mid = call.message.message_id

	if uid not in CLICKED_BY:
		click_kb_edited = types.InlineKeyboardMarkup()
		click_edited = types.InlineKeyboardButton("Спасибо", callback_data='clicked')
		click_kb_edited.row(click_edited)

		bot.edit_message_text("<b>Удаляем напоминание...</b>", cid, mid, reply_markup=click_kb_edited, parse_mode="HTML")

		conn.execute("DELETE from DATA where id=? and EVENT=? ", (delete_conditions[0], delete_conditions[1],))
		conn.commit()
		print("удалено", delete_conditions[0], delete_conditions[1])
		delete_conditions.clear()
		
	else:
		bot.answer_callback_query(call.id, text="Вы уже нажали на кнопку")



t = threading.Thread(target=send_reminder)
t.start()

while True:
    try:
        bot.polling(none_stop=True, interval=0)
    except:
        sleep(10)
	

