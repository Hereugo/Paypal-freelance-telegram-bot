import re
import os
import time
from random import *

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TOKEN, messages
from functions import Map

import pymongo
from pymongo import MongoClient

import paypalrestsdk
from paypalrestsdk import Payment

from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

# Telebot
bot = telebot.TeleBot(TOKEN)

# Flask
URI = 'mongodb+srv://Amir:2LSCfSNcwAz9x3!@cluster0.jxsw1.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
URL = 'https://paypal-telegram-fiverr-bot.herokuapp.com/'
app = Flask(__name__)
cluster = PyMongo(app, uri=URI)
collection = cluster.db.user


# Paypal python sdk
paypalrestsdk.configure({
	"mode": "sandbox", # sandbox or live
	"client_id": "AW7Q6ChzzOnd5wa8OuYbiP5RiaqQ6tumVR7UTlMLaDIF_FXRhxo77BaNmjgQfKN6GBLK5c2rDHiijpHv",
	"client_secret": "EBBmQczfJM6WrweaUE-NDMOxpBn__GH_RXtXQB1nwt8AN6doaa7MBEYuf3ok6EREj8AsrL7Eg7vSE4wM",
})


@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
	bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
	print('Good')
	return "!", 200

@app.route('/payment/execute/')
def execute():
	payment_id = request.args['paymentId']
	payer_id = request.args['PayerID']

	payment = paypalrestsdk.Payment.find(payment_id)
	[desc, uid1, uid2, offer_id] = payment['transactions'][0]['description'].split('#')
	print(desc, uid1, uid2)
	if payment.execute({'payer_id': payer_id}):
		print('Payment was successful')
		msg = bot.send_message(int(uid2), 'Payment was successful\n Order has been started!')


		bot.send_message(int(uid1), 'Order has been started!')


		offer = ""
		seller = collection.find_one({'_id': int(uid1)})
		for x in seller['offers']:
			if x['id'] == offer_id:
				offer = x
				break
		order = ""
		for x in seller['gigs']:
			if x['token'] == offer['token']:
				order = x
				break
		order['id'] = offer['id']
		order['duration'] = offer['duration']
		order['start_date'] = time.time()
		order['end_date'] = order['start_date'] + toSeconds(order['duration'])

		print(order)
		collection.update_one({'_id': int(uid1)}, {'$push': {'orders': order}, '$pull': {'offers': {'id': offer['id']}}})
	else:
		print(payment.error)
		msg = bot.send_message(int(uid2), 'Something went wrong, try again later')
	menu(msg)

	return "Payment success!", 200

@app.route('/')
def webhook():
	bot.remove_webhook()
	bot.set_webhook(url=URL + TOKEN)
	return '!', 200

def toSeconds(x):
	return x * 24 * 60 * 60

def newId():
	return str(randint(1, 1e9))

def previous(path):
	return re.search(r'(.+\/)+', path)[0][:-1]

@bot.message_handler(commands=['menu'])
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
			'process_gig': {
				'title':"", 
				'desc':"", 
				'price':"", 
				'token':"#",
			},
			'process_order': {
				'id': newId(),
				'customer': '#',
				'token': "#",
				'duration': "",
			},
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


def create_offer(message, value):
	userId = message.chat.id
	seller = collection.find_one({'gigs.token': value[0]})

	if seller['_id'] == userId:
		bot.send_message(userId, 'Cant make an offer to yourself')
		back(message)
		return

	gig = ""
	for x in seller['gigs']:
		if x['token'] == value[0]:
			gig = x
			break
	print(gig)

	if value[1] == '0':
		msgg = bot.send_message(userId, 'Set your time in days')
		bot.register_next_step_handler(msgg, process_create_offer_time_step)
		return

	buyer = collection.find_one({'_id': userId})
	path = buyer['path']
	collection.update_one({'_id': userId}, {'$set': {'path': previous(path), 'process_order.token': value[0], 'process_order.customer': userId}})


	print(seller, buyer)
	keyboard = InlineKeyboardMarkup()

	keyboard.add(InlineKeyboardButton(messages.create_offer.buttons[0].text, callback_data=messages.create_offer.buttons[0].callback_data.format(value[0], 0)))
	keyboard.add(InlineKeyboardButton(messages.create_offer.buttons[1].text, callback_data=messages.create_offer.buttons[1].callback_data))
	keyboard.add(InlineKeyboardButton(messages.create_offer.buttons[2].text, callback_data=messages.create_offer.buttons[2].callback_data))

	bot.send_message(userId, messages.create_offer.text.format(gig['title'], gig['desc'], gig['price'], seller['name'], buyer['process_order']['duration']), reply_markup=keyboard)
def process_create_offer_time_step(message):
	text = message.text
	userId = message.chat.id

	user = collection.find_one({'_id': userId})
	[query, value] = calc(re.search(r'\w+(|\?[^\/]+)$', user['path'])[0])
	print(query, value, user['path'])
	if value[1] == '0': # Timer
		collection.update_one({'_id': userId}, {'$set': {'process_order.duration': text}})

	create_offer(message, [value[0], '9'])

def create_offer_complete(message):
	userId = message.chat.id

	bot.send_message(userId, messages.create_offer_complete.text[0])

	buyer = collection.find_one({'_id': userId})
	offer = buyer['process_order']
	seller = collection.find_one({'gigs.token': offer['token']})
	print(offer)
	print(seller, buyer)
	collection.update_one({'_id': seller['_id']}, {'$push': {'offers': offer}}) # Send offer to seller
	collection.update_one({'_id': userId}, {'$set': {'process_order': {'id': str(newId()), 'duration': "", 'token': '#'}}}) # Clear process order of buyer

	bot.send_message(seller['_id'], messages.create_offer_complete.text[1].format(buyer['username']))

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

def orders(message, value):
	userId = message.chat.id
	try:	
		orders = collection.find_one({'_id': userId})['orders']
	except:
		bot.send_message(userId, 'No current orders')
		back(message)
		return

	value[0] = int(value[0])
	keyboard = InlineKeyboardMarkup()
	keyboard.row(InlineKeyboardButton(messages.offers.buttons[0].text, callback_data=messages.offers.buttons[0].callback_data.format(max(value[0] - 1, 0))),
				 InlineKeyboardButton(messages.offers.buttons[1].text, callback_data=messages.offers.buttons[1].callback_data.format(min(value[0] + 1, len(offers) - 1))))
	keyboard.add(InlineKeyboardButton(messages.gigs.buttons[3].text, callback_data=messages.gigs.buttons[3].callback_data))
	keyboard.add(InlineKeyboardButton(messages.gigs.buttons[4].text, callback_data=messages.gigs.buttons[4].callback_data))

	bot.send_message(userId, messages.orders.text.format(orders[value[0]]['title'], orders[value[0]]['desc'], orders[value[0]]['price'], orders[value[0]]['duration'], "DD"), reply_markup=keyboard)

def offers(message, value):
	userId = message.chat.id
	try:	
		offers = collection.find_one({'_id': userId})['offers']
	except:
		bot.send_message(userId, 'No offers')
		back(message)
		return
	value[0] = int(value[0])

	keyboard = InlineKeyboardMarkup()
	keyboard.row(InlineKeyboardButton(messages.offers.buttons[0].text, callback_data=messages.offers.buttons[0].callback_data.format(max(value[0] - 1, 0))),
				 InlineKeyboardButton(messages.offers.buttons[1].text, callback_data=messages.offers.buttons[1].callback_data.format(min(value[0] + 1, len(offers) - 1))))
	keyboard.row(InlineKeyboardButton(messages.offers.buttons[2].text, callback_data=messages.offers.buttons[2].callback_data.format(offers[value[0]]['id'])),
				 InlineKeyboardButton(messages.offers.buttons[3].text, callback_data=messages.offers.buttons[3].callback_data.format(offers[value[0]]['id'])))
	keyboard.add(InlineKeyboardButton(messages.gigs.buttons[4].text, callback_data=messages.gigs.buttons[4].callback_data))

	gig = ""
	token = offers[value[0]]['token']
	for x in collection.find_one({'gigs.token': token})['gigs']:
		if x['token'] == token:
			gig = x
			break

	print(gig, offers[value[0]])
	bot.send_message(userId, messages.offers.text.format(gig['title'], gig['desc'], gig['price'], offers[value[0]]['duration']), reply_markup=keyboard)

def accept_offer(message, value):
	userId = message.chat.id

	bot.send_message(userId, 'Wait for an order to start')

	seller = collection.find_one({'_id': userId})
	offer = ""
	for x in seller['offers']:
		if x['id'] == value[0]:
			offer = x
			break
	print(offer)
	gig = ""
	for x in seller['gigs']:
		if x['token'] == offer['token']:
			gig = x
			break
	print(gig)


	payment = Payment({
		'intent': 'sale',
		'payer': {
			'payment_method': 'paypal',
		},
		'redirect_urls': {
	        "return_url": URL + "payment/execute/",
	        "cancel_url": URL,
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
				'description': '{}\n\n Duration: {} days#{}#{}#{}'.format(gig['desc'], offer['duration'], seller['_id'], offer['customer'], offer['id']),
			}
		]
	})
	if payment.create():
		print("Payment created successfully")
		for link in payment.links:
			if link.rel == "approval_url":
				approval_url = str(link.href)
				print("Redirect for approval: %s" % (approval_url))
				bot.send_message(offer['customer'], 'Offer {} was accepted\n To begin this order pay using this link {}'.format(offer['id'], approval_url))
	else:
		bot.send_message(userId, 'Something went wrong')

def decline_offer(message, value):
	userId = message.chat.id

	bot.send_message(userId, 'Offer was declined')

	seller = collection.find_one({'_id': userId})
	offer = ""
	for x in seller['offers']:
		if x['id'] == value[0]:
			offer = x
			break

	collection.update_one({'_id': userId}, {'$pull': {'offers': {'id': offer['id']}}})
	bot.send_message(offer['customer'], '{} has declined your offer'.format(seller['username']))

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
	path = user['path']

	if value[0] == '0': # Title
		msgg = bot.send_message(userId, 'Typin your Title')
		bot.register_next_step_handler(msgg, process_create_new_gig_step)
		return
	elif value[0] == '1': # Description
		msgg = bot.send_message(userId, 'Typin your gigs description')
		bot.register_next_step_handler(msgg, process_create_new_gig_step)
		return
	elif value[0] == '2': # Price
		msgg = bot.send_message(userId, 'Set your price')
		bot.register_next_step_handler(msgg, process_create_new_gig_step)
		return

	collection.update_one({'_id': userId}, {'$set': {'path': previous(path)}})

	keyboard = InlineKeyboardMarkup()
	for button in messages.create_new_gig.buttons:
		keyboard.add(InlineKeyboardButton(button.text, callback_data=button.callback_data))

	gig = collection.find_one({'_id': userId})['process_gig']
	bot.send_message(userId, messages.create_new_gig.text.format(gig['title'], gig['desc'], gig['price']), reply_markup=keyboard)

def process_create_new_gig_step(message):
	text = message.text
	userId = message.chat.id

	user = collection.find_one({'_id': userId})
	[query, value] = calc(re.search(r'\w+(|\?[^\/]+)$', user['path'])[0])
	print(query, value, user['path'])
	if value[0] == '0': # Title
		collection.update_one({'_id': userId}, {'$set': {'process_gig.title': text}})
	elif value[0] == '1': # Description
		collection.update_one({'_id': userId}, {'$set': {'process_gig.desc': text}})
	elif value[0] == '2': # Price
		collection.update_one({'_id': userId}, {'$set': {'process_gig.price': text}})

	create_new_gig(message, ['9'])

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
	path = user['path']

	if value[0] == '0': # Name
		msgg = bot.send_message(userId, 'Typin your name')
		bot.register_next_step_handler(msgg, process_register_step)
		return
	elif value[0] == '1': # Paypal account
		msgg = bot.send_message(userId, 'Typin your paypal account')
		bot.register_next_step_handler(msgg, process_register_step)
		return
	elif value[0] == '2': # Profile Description
		msgg = bot.send_message(userId, 'Typin your profile description')
		bot.register_next_step_handler(msgg, process_register_step)
		return

	collection.update_one({'_id': userId}, {'$set': {'path': previous(path)}})
	keyboard = InlineKeyboardMarkup()
	for button in messages.register.buttons:
		keyboard.add(InlineKeyboardButton(button.text, callback_data=button.callback_data))

	user = collection.find_one({'_id': userId})
	bot.send_message(userId, messages.register.text.format(user['name'], user['paypal_account'], user['profile_desc']), reply_markup=keyboard)

def process_register_step(message):
	text = message.text
	userId = message.chat.id

	user = collection.find_one({'_id': userId})
	[query, value] = calc(re.search(r'\w+(|\?[^\/]+)$', user['path'])[0])
	print(query, value, user['path'])
	if value[0] == '0': # Name
		collection.update_one({'_id': userId}, {'$set': {'name': text}})
	elif value[0] == '1': # Paypal account
		collection.update_one({'_id': userId}, {'$set': {'paypal_account': text}})
	elif value[0] == '2': # Profile Description
		collection.update_one({'_id': userId}, {'$set': {'profile_desc': text}})

	register(message, ['9'])

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


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))