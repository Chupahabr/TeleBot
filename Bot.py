#!/usr/bin/python
# -- coding: utf-8 --

import logging
import re
import os
import datetime
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor 
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from sql import SQLighter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
api = '1443203441:AAFRhMKXPAdshPxnt6gIlfwOOWtSi_81DBk'
global num
num = 0

logging.basicConfig(level=logging.INFO)
bot = Bot(token=api)
dp = Dispatcher(bot)
print(os.getcwd())
db = SQLighter(os.getcwd()+'/Pharmacy.db')
phars = db.output("select * from Pharmacy")
class buf:
	def __init__(self):
		self.ar=[]
		self.search_list=[]
		self.phars=[]
		self.basket=dict()
		self.user_loc=""
		self.phar_id=[0,""]
bufer=buf()
bufer.phars=phars


def keyboardInfo(kb, ar, ty):
	cont = ""
	for item in ar[num : num + 6]:
		if ty=="pill":
			cont = item[4]
			key= InlineKeyboardButton(cont,callback_data=ty+str(item[0]))
		elif ty=="phar":
			cont = item[1]
			key= InlineKeyboardButton(cont,callback_data=ty+str(item[0]))
		elif ty=="del_":
			cont=item[1]
			key= InlineKeyboardButton(cont,callback_data=ty+str(item[0]))
		kb.add(key)
	if num != 0:
		kb.row(InlineKeyboardButton(text="Предыдущие", callback_data="move_back"),InlineKeyboardButton(text="Следующие", callback_data="move_next"))
	else:
		kb.add(InlineKeyboardButton(text="Следующие", callback_data="move_next"))
	return kb

@dp.message_handler(commands=['start','help']) # Это вывод строк на команду /start и /help
async def send_welcome(message: types.Message):
	if(message.text=="/start"):
		bufer.ar=[]
		bufer.search_list=[]
		bufer.basket[message.from_user.id]=[]
		kbm= ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton("Выбрать в ручную"))
		await bot.send_message(message.from_user.id,"Здравствуйте. Я ваш личный помощник в выборе лекарств.\nПожалуйста, выберите нажмите кнопку, для выбора аптеки.", reply_markup=kbm)
	elif message.text=="/help":
		await bot.send_message(message.from_user.id, """ - сразу после запуска чат-бота необходимо выбрать аптеку
 \n- наберите /start - начало работы с ботом
 \n- выберите способ поиска аптеки кнопками 'Вручную' или 'Найти ближайшую'
 \n- следуйте инструкциям
 \n- выберите действие: поиск лекарств или вызов корзины покупок соответствующими кнопками
 \n- для поиска введите название товара и выберите из представленного списка нужный
 \n- следуйте инструкциям
 \n- укажите количество товара по образцу: 'шт:3'(без кавычек) или просто число
 \n- для вызова 'Корзины' нажмите соответствующую кнопку или введите сообщение 'Корзина'(без кавычек)
 \n- для подтверждения заказа нажмите кнопку 'Оформить заказ'
 \n- для удаления товара из корзины нажмите соответствующую кнопку и выберите товар, котoрый хотите удалить""")

@dp.message_handler(content_types=["text"])
async def getmessage(message: types.Message):
	ikb1=InlineKeyboardMarkup(row_width=2, resize_keyboard=True)
	if message.text=="Выбрать в ручную":
		ikb1 = keyboardInfo(ikb1, bufer.phars, "phar")
		await bot.send_message(message.from_user.id, f"Список аптек {num+1} - {len(bufer.phars) if num + 6 > len(bufer.phars) else num + 6 if num!=0 else 0} из {len(bufer.phars)} ", reply_markup=ikb1)
	elif (message.text=="Поиск"):
		bufer.search_list=[]
		await bot.send_message(message.from_user.id, "Введите название лекарства")
	elif message.text == "Корзина":
		if bufer.basket[message.from_user.id]!=[]:
			ikb1.add(InlineKeyboardButton(text="Оформить заказ", callback_data="order")).add(InlineKeyboardButton(text="Удалить лот", callback_data="delit"))
			summa = 0
			text = ""
			text="Список выбранных товаров:\n" 
			for item in bufer.basket[message.from_user.id]:
				stroka=f"{item[1]} количество: {item[3]} цена: {item[2]}\n"
				text += stroka
				summa += int(item[2])*int(item[3])
			text += f'Итоговая стоимость {summa}'
			await bot.send_message(chat_id=message.chat.id,text=text, reply_markup=ikb1)
		else:
			await bot.send_message(message.from_user.id, "Корзина пуста")
	elif (message.text.lower().startswith("шт:") or (message.text.isdigit())):
		i=""
		for key in bufer.basket:
			i=key        
		pill_id=i
		if message.text.isdigit():
			col=message.text
		else:
			col=message.text[3:]
		bufer.basket[message.from_user.id][-1].append(col)
		await bot.send_message(message.from_user.id, 'Добавлено')
	else:
		bufer.search_list=[]
		sear=message.text.split(" ")
		for pill in bufer.ar:
			for j in sear:
				if (j.lower() in pill[4].lower()):
					bufer.search_list.append(pill)
		keyboardInfo(ikb1, bufer.search_list, "pill")
		stroka=""
		s=bufer.search_list[num:num+6]
		for pill in s:
			stroka+=str(f"{pill[4]} производства: {pill[5]} цена: {pill[2]}\n")         
		await bot.send_message(message.from_user.id, f"Список лекарств {num+1} - {len(bufer.search_list) if num + 6 > len(bufer.search_list) else num +6  if num!=0 else 0} из {len(bufer.search_list)} :\n{stroka}", reply_markup=ikb1)

			
@dp.callback_query_handler(lambda c: c.data == "order")
async def callback_order(callback_query: types.CallbackQuery):
	await bot.edit_message_text(chat_id=callback_query.message.chat.id, text=callback_query.message.text, reply_markup=None, message_id=callback_query.message.message_id)
	vals=""
	summa=0
	for item in bufer.basket[callback_query.from_user.id]:
		summa+=item[2]
	db.output(f"insert into OrdersInformation(orderamount,orderstatus,data,custid) values({summa},'Ожидание', '{datetime.date.today()}','{callback_query.from_user.id}')")
	or_id=db.output(f"select id from OrdersInformation where custid={callback_query.from_user.id} order by id desc limit 1")[0][0]
	for item in bufer.basket[callback_query.from_user.id]:
		stroka=f"({or_id},{item[0]},{item[3]}),"
		vals+=stroka	
	db.output(f"insert into orders(CodeOrdersInformation, codemedicines,numberofmedications) values{vals[:len(vals)-1]}")
	await bot.send_message(callback_query.from_user.id, f"Ваш заказ внесен в базу. Номер заказа: {or_id}, забрать можно по адресу:\n{bufer.phar_id[1]}")
	del bufer.basket[callback_query.from_user.id]

@dp.callback_query_handler(lambda c: c.data.startswith('del')) # Если callback del
async def process_delitem(callback_query: types.CallbackQuery):
	await bot.edit_message_text(chat_id=callback_query.message.chat.id, text=callback_query.message.text, reply_markup=None, message_id=callback_query.message.message_id)
	ikb1=InlineKeyboardMarkup(row_width=2)
	if callback_query.data.startswith("delit"):
		ikb1= keyboardInfo(ikb1,bufer.basket[callback_query.from_user.id],"del_")
		await bot.send_message(callback_query.from_user.id, f"Выберите лот который хотите удалить: {num+1} - {len(bufer.basket[callback_query.from_user.id]) if num + 6 > len(bufer.basket[callback_query.from_user.id]) else num + 6 if num!=0 else 0} из {len(bufer.basket[callback_query.from_user.id])} ", reply_markup= ikb1)
	elif callback_query.data.startswith("del_"):
		for i in bufer.basket[callback_query.from_user.id]:
			if i[0]==callback_query.data[4:]:
				bufer.basket[callback_query.from_user.id].remove(i)
				break
		await bot.send_message(callback_query.from_user.id, "Лот успешно удалён")

@dp.callback_query_handler(lambda c: c.data.startswith('pill')) # Если callback таблеточка
async def process_callback_button1(callback_query: types.CallbackQuery):
	await bot.edit_message_text(chat_id=callback_query.message.chat.id, text=callback_query.message.text, reply_markup=None, message_id=callback_query.message.message_id)
	pill_id=callback_query.data[4::]
	price=0
	name=""
	for pill in bufer.search_list:
			if (str(pill[0])==str(pill_id)):
				price=pill[2]
				name=pill[4]
				break
	if callback_query.from_user.id in bufer.basket:
		bufer.basket[callback_query.from_user.id].append([pill_id,name,price])
	else:
		bufer.basket[callback_query.from_user.id] = [[pill_id,name , price]]
	await bot.send_message(callback_query.from_user.id, text="Введите количество лекарств. Пример: Шт:8 или 8" )


@dp.callback_query_handler(lambda c: c.data.startswith('phar')) # Если callback аптеки
async def process_callback_button2(callback_query: types.CallbackQuery):
	await bot.edit_message_text(chat_id=callback_query.message.chat.id, text=callback_query.message.text, reply_markup=None, message_id=callback_query.message.message_id)
	bufer.phar_id[0]=callback_query.data[4:]
	for i in bufer.phars:
		if i[0]==bufer.phar_id[0]:
			bufer.phar_id[1]=i[1]
			break;
	d=db.output(f"SELECT * FROM medicines where idphar={bufer.phar_id[0]}")
	bufer.ar=d
	kb = ReplyKeyboardMarkup(resize_keyboard=True)
	k1 = KeyboardButton(text="Поиск")
	k2 = KeyboardButton(text="Корзина") 
	kb.row(k1, k2)
	await bot.send_message(callback_query.from_user.id, text="Вы выбрали аптеку, нажмите 'Поиск' для дальнейших действий.", reply_markup=kb)
@dp.callback_query_handler(lambda c: c.data.startswith('move')) # Переход списков
async def callback_button_move(callback_query: types.CallbackQuery):
	global num
	await bot.edit_message_text(chat_id=callback_query.message.chat.id, text=callback_query.message.text, reply_markup=None, message_id=callback_query.message.message_id)
	if callback_query.data[5:]=="back":
		num -= 6
		if num < 0:
			num = 0
	elif callback_query.data[5:]=="next":
		num += 6
		if len(bufer.ar)==0:
			if num>=len(bufer.phars):
				num=len(bufer.phars) - 6
		else:
			if num >= len(bufer.search_list):
				num = len(bufer.search_list) - 6
	ikb1=InlineKeyboardMarkup(row_width=1)
	if (callback_query.message.text.startswith("Список лекарств")):
		ikb1 = keyboardInfo(ikb1, bufer.search_list, "pill")
		await bot.send_message(callback_query.from_user.id, f"Список лекарств {num+1} - {len(bufer.search_list) if num + 6 > len(bufer.search_list) else num + 7} из {len(bufer.search_list)} ", reply_markup=ikb1)
	elif (callback_query.message.text.startswith("Список аптек")):
		ikb1 = keyboardInfo(ikb1, bufer.phars, "phar")
		await bot.send_message(callback_query.from_user.id, f"Список аптек {num+1} - {len(bufer.phars) if num + 6 > len(bufer.phars) else num + 7} из {len(bufer.phars)} ", reply_markup=ikb1)
	elif (callback_query.message.text.startswith("Выберите пункт")):
		ikb1 = keyboardInfo(ikb1, bufer.basket[callback_query.from_user.id], "del_")
		await bot.send_message(callback_query.from_user.id, f"Выберите лот который хотите удалить: {num+1} - {len(bufer.basket[callback_query.from_user.id]) if num + 6 > len(bufer.basket[callback_query.from_user.id]) else num + 7 if num!=0 else 0} из {len(bufer.phars)} ", reply_markup=ikb1)

if __name__ == '__main__':
	executor.start_polling(dp, skip_updates=True)

