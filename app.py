import re
from random import *

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import token, messages
from functions import Map

import pymongo
from pymongo import MongoClient

import paypalrestsdk
from paypalrestsdk import Payment

from flask import Flask, jsonify, request


# Telebot
bot = telebot.TeleBot(token, threaded=False)

#Mongo DB
cluster = MongoClient('mongodb+srv://Amir:2LSCfSNcwAz9x3!@cluster0.jxsw1.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
db = cluster['telegram']
collection = db['user']

# Paypal python sdk
paypalrestsdk.configure({
	"mode": "sandbox", # sandbox or live
	"client_id": "AW7Q6ChzzOnd5wa8OuYbiP5RiaqQ6tumVR7UTlMLaDIF_FXRhxo77BaNmjgQfKN6GBLK5c2rDHiijpHv",
	"client_secret": "EBBmQczfJM6WrweaUE-NDMOxpBn__GH_RXtXQB1nwt8AN6doaa7MBEYuf3ok6EREj8AsrL7Eg7vSE4wM",
})

# Flask
app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/bot', methods=['POST'])
def botting():
	update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
	bot.process_new_updates([update])
	return '!', 200

@app.route('/payment/execute')
def execute():
	payment_id = request.args['paymentId']
	payer_id = request.args['PayerID']

	payment = paypalrestsdk.Payment.find(payment_id)
	if payment.execute({'payer_id': payer_id}):
		print('Payment was successful')
	else:
		print(payment.error)

@app.route('/')
def webhook():
	bot.remove_webhook()
	bot.set_webhook(url='https://paypal-telegram-fiverr-bot.herokuapp.com/bot')
	return '?', 200


def newId():
	return str(randint(1, 1e9))

def previous(path):
	return re.search(r'(.+\/)+', path)[0][:-1]

@bot.message_handler(commands=['start'])
def menu(message):
	userId = message.chat.id
	result = collection.find_one({'_id': userId})
	if result == None:
		user = {
			'_id': userId, 
			'registered': False,
			'name': '',
			'paypal_account': '',
			'profile_desc': '',
			'path': 'menu',
			'last_message': {
				'text': "",
				"id": "",
			},
			'process_gig': {
				'title':"", 
				'desc':"", 
				'price':"", 
				'token':"#",
			}
		}
		collection.insert_one(user)

	collection.update_one({'_id': userId}, {'$set': {'path': 'menu'}})

	keyboard = InlineKeyboardMarkup()
	for button in messages['menu']['buttons']:
		keyboard.add(InlineKeyboardButton(button.text, callback_data=button.callback_data))
	bot.send_message(userId, messages.menu.text, reply_markup=keyboard)

@bot.message_handler(commands=['back'])
def back(message):
	callback_query(Map({'message': message, 'data': 'back'}))

def checkRegistration(message, user):
	userId = message.chat.id
	if not user['registered']:
		path = collection.find_one({'_id': userId})['path']
		path = previous(path) + '/register'
		collection.update_one({'_id': userId}, {'$set': {'path': path}})
		register(message, ['9'])
		return True
	return False

def profile_buyer(message):
	userId = message.chat.id
	user = collection.find_one({'_id': userId})
	if checkRegistration(message, user):
		return

	keyboard = InlineKeyboardMarkup()
	for button in messages.profile_buyer.buttons:
		keyboard.add(InlineKeyboardButton(button.text, callback_data=button.callback_data))
	bot.send_message(userId, messages.profile_buyer.text.format(user['name'], user['paypal_account']), reply_markup=keyboard)

def search_order(message, value=-1):
	userId = message.chat.id
	
	if value == -1:
		keyboard = InlineKeyboardMarkup()
		keyboard.add(InlineKeyboardButton('Back', callback_data='back'))
		msg = bot.send_message(userId, "Please send a given token here", reply_markup=keyboard)
		bot.register_next_step_handler(msg, process_search_order_step)
	else:
		process_search_order_step(message, value[0])
def process_search_order_step(message, token=""):
	userId = message.chat.id
	if token == "":
		token = message.text

	user = collection.find_one({'gigs.token': token})
	if user == None:
		keyboard = InlineKeyboardMarkup()
		keyboard.add(InlineKeyboardButton('Back', callback_data='back'))
		msg = bot.send_message(userId, 'Invalid token', reply_markup=keyboard)
		return

	gig = ""
	for x in user['gigs']:
		if x['token'] == token:
			gig = x
			break

	keyboard = InlineKeyboardMarkup()
	collection.update_one({'_id': userId}, {'$set': {'path': 'menu/profile_buyer/search_order?{}'.format(token)}})
	keyboard.add(InlineKeyboardButton(messages.search_order.buttons[0].text, callback_data=messages.search_order.buttons[0].callback_data.format(token)))
	keyboard.add(InlineKeyboardButton(messages.search_order.buttons[1].text, callback_data=messages.search_order.buttons[1].callback_data.format(user['_id'])))
	keyboard.add(InlineKeyboardButton(messages.search_order.buttons[2].text, callback_data=messages.search_order.buttons[2].callback_data))

	bot.send_message(userId, messages.search_order.text.format(gig['title'], gig['desc'], gig['price'], user['name']), reply_markup=keyboard)

def buy_order(message, token):
	userId = message.chat.id
	user = collection.find_one({'gigs.token': token})
	gig = ""
	for x in user['gigs']:
		if x['token'] == token:
			gig = x
			break
	payment = Payment({
		'intent': 'sale',
		'payer': {
			'payment_method': 'paypal',
		},
		'redirect_urls': {
	        "return_url": "{}payment/execute/".format(url),
	        "cancel_url": "{}".format(url),
		},
		'transactions': [
			{
				'item_list': {
					'items': [
						{
							'name': gig['title'],
							'sku': "WHAT IS IT SKU",
							'price': '{}.00'.format(gig['price']),
							'currency': 'USD',
							'quantity': 1
						}
					]
				},
				'amount': {
					'total': '{}.00'.format(gig['price']),
					'currency': 'USD'
				},
				'description': gig['desc'],
			}
		]
	})
	if payment.create():
		print("Payment created successfully")
		for link in payment.links:
			if link.rel == "approval_url":
				approval_url = str(link.href)
				print("Redirect for approval: %s" % (approval_url))
				bot.send_message(userId, 'Go to this link to complete the order: %s' % (approval_url))
	else:
		bot.send_message(userId, 'Something went wrong')

def see_profile(message, value):
	userId = message.chat.id
	user = collection.find_one({'_id': int(value[0])})

	keyboard = InlineKeyboardMarkup()
	keyboard.add(InlineKeyboardButton(messages.see_profile.buttons[0].text, callback_data=messages.see_profile.buttons[0].callback_data.format(value[0])))
	keyboard.add(InlineKeyboardButton(messages.see_profile.buttons[1].text, callback_data=messages.see_profile.buttons[1].callback_data))
	keyboard.add(InlineKeyboardButton(messages.see_profile.buttons[2].text, callback_data=messages.see_profile.buttons[2].callback_data))	

	bot.send_message(userId, messages.see_profile.text.format(user['name'], user['profile_desc']), reply_markup=keyboard)

def start_conversation(message, value): 
	userId = message.chat.id
	user = collection.find_one({'_id': int(value[0])})

	keyboard = InlineKeyboardMarkup()
	for button in messages.start_conversation.buttons:
		keyboard.add(InlineKeyboardButton(button.text, callback_data=button.callback_data))
	bot.send_message(userId, messages.start_conversation.text.format(user['username']), reply_markup=keyboard)

####### SELLERS SYSTEM ########
def profile_seller(message):
	userId = message.chat.id
	user = collection.find_one({'_id': userId})
	if checkRegistration(message, user):
		return

	keyboard = InlineKeyboardMarkup()
	for button in messages.profile_seller.buttons:
		keyboard.add(InlineKeyboardButton(button.text, callback_data=button.callback_data))
	bot.send_message(userId, messages.profile_seller.text.format(user['name'], user['paypal_account'], user['profile_desc']), reply_markup=keyboard)

def gigs(message, value):
	userId = message.chat.id
	try:	
		gigs = collection.find_one({'_id': userId})['gigs']
	except:
		bot.send_message(userId, 'No gigs were made')
		back(message)
		return
	value[0] = int(value[0])

	keyboard = InlineKeyboardMarkup()
	keyboard.row_width = 3
	keyboard.row(InlineKeyboardButton(messages.gigs.buttons[0].text, callback_data=messages.gigs.buttons[0].callback_data.format(max(value[0] - 1, 0), value[1])),
				 InlineKeyboardButton(messages.gigs.buttons[2].text, callback_data=messages.gigs.buttons[2].callback_data.format(min(value[0] + 1, len(gigs) - 1), value[1])))
	if value[1] == '1':
		keyboard.add(InlineKeyboardButton(messages.gigs.buttons[1].text, callback_data=messages.gigs.buttons[1].callback_data.format(value[0])))
	keyboard.add(InlineKeyboardButton(messages.gigs.buttons[3].text, callback_data=messages.gigs.buttons[3].callback_data.format(value[0])))
	keyboard.add(InlineKeyboardButton(messages.gigs.buttons[4].text, callback_data=messages.gigs.buttons[4].callback_data))

	bot.send_message(userId, messages.gigs.text.format(gigs[value[0]]['title'], gigs[value[0]]['desc'], gigs[value[0]]['price']), reply_markup=keyboard)

def token_reciever(message, value):
	userId = message.chat.id
	value = int(value[0])
	gig = collection.find_one({'_id': userId})['gigs'][value]
	keyboard = InlineKeyboardMarkup()
	for button in messages.token_reciever.buttons:
		keyboard.add(InlineKeyboardButton(button.text, callback_data=button.callback_data))
	bot.send_message(userId, messages.token_reciever.text.format(gig['token']), reply_markup=keyboard)

def edit_gig(message, value):
	userId = message.chat.id
	gig = collection.find_one({'_id': userId})['gigs'][int(value[1])]
	collection.update_one({'_id': userId}, {'$set': {'process_gig': gig}})
	create_new_gig(message, value)
###############################

## CREATE NEW GIG SYSTEM ##
def create_new_gig(message, value):
	userId = message.chat.id
	user = collection.find_one({'_id': userId})
	msg = user['last_message']
	path = user['path']

	if value[0] != '9':
		try:
			bot.delete_message(userId, msg['id'])
		except:
			pass


	collection.update_one({'_id': userId}, {'$set': {'path': previous(path)}})

	if value[0] == '0': # Title
		collection.update_one({'_id': userId}, {'$set': {'process_gig.title': msg['text']}})
	elif value[0] == '1': # Description
		collection.update_one({'_id': userId}, {'$set': {'process_gig.desc': msg['text']}})
	elif value[0] == '2': # Price
		collection.update_one({'_id': userId}, {'$set': {'process_gig.price': msg['text']}})

	keyboard = InlineKeyboardMarkup()
	for button in messages.create_new_gig.buttons:
		keyboard.add(InlineKeyboardButton(button.text, callback_data=button.callback_data))

	gig = collection.find_one({'_id': userId})['process_gig']
	bot.send_message(userId, messages.create_new_gig.text.format(gig['title'], gig['desc'], gig['price']), reply_markup=keyboard)

def create_new_gig_complete(message):
	userId = message.chat.id

	gig = collection.find_one({'_id': userId})['process_gig']
	if gig['token'] != '#':
		collection.update_one({'_id': userId, 'gigs.token': gig['token']}, {'$set': {'gigs.$.title': gig['title'], 'gigs.$.desc': gig['desc'], 'gigs.$.price': gig['price']}})
	else:
		gig['token'] = newId()
		collection.update_one({'_id': userId}, {'$push': {'gigs': gig}})

	collection.update_one({'_id': userId}, {'$set': {'process_gig':{'title':"", 'desc':"", 'price':"", 'token':"#"}}}) # clear process_gig

	msg = bot.send_message(userId, 'Gig has been saved!')
	collection.update_one({'_id': userId}, {'$set': {'path': 'menu/profile_seller'}})
	profile_seller(msg)
############################

## REGISTERATION SYSTEM ##

def register(message, value):
	userId = message.chat.id
	user = collection.find_one({'_id': userId})
	msg = user['last_message']
	path = user['path']

	if value[0] != '9':
		try:
			bot.delete_message(userId, msg['id'])
		except:
			pass


	collection.update_one({'_id': userId}, {'$set': {'path': previous(path)}})

	if value[0] == '0': # Name
		collection.update_one({'_id': userId}, {'$set': {'name': msg['text']}})
	elif value[0] == '1': # Paypal account
		collection.update_one({'_id': userId}, {'$set': {'paypal_account': msg['text']}})
	elif value[0] == '2': # Profile Description
		collection.update_one({'_id': userId}, {'$set': {'profile_desc': msg['text']}})

	keyboard = InlineKeyboardMarkup()
	for button in messages.register.buttons:
		keyboard.add(InlineKeyboardButton(button.text, callback_data=button.callback_data))

	user = collection.find_one({'_id': userId})
	bot.send_message(userId, messages.register.text.format(user['name'], user['paypal_account'], user['profile_desc']), reply_markup=keyboard)

def register_complete(message):
	userId = message.chat.id

	user = collection.find_one({'_id': userId})
	if user['name'] == '' or user['paypal_account'] == '':
		bot.send_message('Fill in your profile')
		register(message, ['9'])
		return
	val = {
		'path': 'menu',
		'username': message.from_user.username,
		'registered': True,
	}
	collection.update_one({'_id': userId}, {'$set': val}) # set profile description

	bot.send_message(userId, "Registration completed!")

	menu(message)
############################

def calc(query):
	value = -1
	if '?' in query:
		value = re.search(r'\?.+', query)[0][1:].split(',')
		query = re.search(r'^[^\?]+', query)[0]
	return [query, value]

def back(message):
	userId = message.chat.id

	path = collection.find_one({'_id': userId})['path']

	path = previous(path) # get rid of /back
	path = previous(path) # get rid of the current dr

	collection.update_one({'_id': userId}, {'$set': {'path': path}})
	query = re.search(r'\w+(|\?[^\/]+)$', path)[0] # name

	[query, value] = calc(query)

	possibles = globals().copy()
	possibles.update(locals())
	method = possibles.get(query)

	if value == -1:
		method(message)
	else:
		method(message, value)


@bot.message_handler(func=lambda message: True)
def message_processer(message):
	userId = message.chat.id
	collection.update_one({'_id': userId}, {'$set': {'last_message': {'text': message.text, 'id': message.message_id}}})

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
	userId = call.message.chat.id
	path = collection.find_one({'_id': userId})['path']

	query = re.search(r'\w+(|\?[^\/]+)$', path)[0]

	if calc(call.data)[0] == calc(query)[0]:
		path = previous(path)
	path = path + '/' + call.data
	collection.update_one({'_id': userId}, {'$set': {'path': path}})

	[query, value] = calc(call.data)

	print(path, value)

	possibles = globals().copy()
	possibles.update(locals())
	method = possibles.get(query)
	if value == -1:
		method(call.message)
	else:
		method(call.message, value)

app.run(host="0.0.0.0", port=os.environ.get('PORT', 80))