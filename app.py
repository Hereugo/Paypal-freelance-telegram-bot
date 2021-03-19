import re
import os
import time

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import paypalrestsdk
from paypalrestsdk import Payment, Payout

from flask import Flask, jsonify, request
from flask_pymongo import PyMongo

from config import TOKEN, messages, URI, URL, CLIENT_ID, CLIENT_SECRET, CURRENCY
from functions import *

# Telebot
bot = telebot.TeleBot(TOKEN)

# Flask
app = Flask(__name__)
cluster = PyMongo(app, uri=URI)
collection = cluster.db.user
collection_dispute = cluster.db.dispute
collection_times = cluster.db.time
empty_key = [[''], ['']]

# Paypal python sdk
paypalrestsdk.configure({
	"mode": "sandbox", # sandbox or live
	"client_id": CLIENT_ID,
	"client_secret": CLIENT_SECRET,
})


@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
	bot.enable_save_next_step_handlers(delay=2)
	bot.load_next_step_handlers()
	bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
	return "!", 200

@app.route('/payment/execute/')
def execute():
	payment_id = request.args['paymentId']
	payer_id = request.args['PayerID']

	payment = paypalrestsdk.Payment.find(payment_id)
	[desc, uid1, uid2, offer_id] = payment['transactions'][0]['description'].split('#')
	print(desc, uid1, uid2)
	uid1 = int(uid1)
	uid2 = int(uid2)
	if payment.execute({'payer_id': payer_id}):
		print('Payment was successful')
		msg = bot.send_message(uid2, messages.payment_execute.text.buyer[0])

		bot.send_message(uid1, messages.payment_execute.text.seller[0])


		seller = collection.find_one({'_id': uid1})
		offer = getFromArrDict(seller['offers'], 'id', offer_id)
		order = getFromArrDict(seller['gigs'], 'token', offer['token'])
		t = time.time()
		order.update({
			'status': 'open',
			'buyer_id': uid2,
			'seller_id': uid1,
			'id': offer['id'],
			'duration': '2',
			'start_time': t,
			'end_date': t + toSeconds(int('2'))
		})

		print(order)
		collection.update_one({'_id': uid1}, {'$push': {'seller_orders': order}, '$pull': {'offers': {'id': offer['id']}}})
		collection.update_one({'_id': uid2}, {'$push': {'buyer_orders': order}})
	else:
		print(payment.error)
		msg = bot.send_message(uid2, messages.payment_execute.text.buyer[0])

	return "Payment success!", 200

@app.route('/')
def webhook():
	bot.remove_webhook()
	bot.set_webhook(url=URL + TOKEN)
	return '!', 200

def checkRegistration(message, user):
	userId = message.chat.id
	if not user['registered']:
		collection.update_one({'_id': userId}, {'$set': {'path': 'menu/register'}})
		register(message)
		return True
	return False

def create_keyboard(arr, vals):
	keyboard = InlineKeyboardMarkup()
	i = 0
	for lst in arr:
		buttons = []
		for button in lst:
			if len(vals[i]) != 3 or vals[i][2]['show'] == '1':
				buttons.append(InlineKeyboardButton(button.text.format(*vals[i][0]), callback_data=button.callback_data.format(*vals[i][1])))
			i = i + 1
		keyboard.row(*buttons)
	return keyboard

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
			'process_gig': {
				'title':"", 
				'desc':"", 
				'price':"", 
				'token':"#",
			},
			
			'function_name': "",
			'use_function': False,

			'process_order': {
				'id': newId(),
				'customer': '#',
				'token': "#",
				'duration': "",
			},
		}
		collection.insert_one(user)

	collection.update_one({'_id': userId}, {'$set': {'path': 'menu'}})
	user = collection.find_one({'_id': userId})

	if checkRegistration(message, user):
		return

	keyboard = create_keyboard(messages.menu.buttons, [empty_key, empty_key])
	bot.send_message(userId, messages.menu.text, reply_markup=keyboard)

@bot.message_handler(commands=['back'])
def back(message):
	callback_query(Map({'message': message, 'data': 'back'}))

####### BUYERS SYSTEM ########
def profile_buyer(message):
	userId = message.chat.id
	user = collection.find_one({'_id': userId})
	keyboard = create_keyboard(messages.profile_buyer.buttons, [empty_key, empty_key, empty_key])
	bot.send_message(userId, messages.profile_buyer.text.format(user['name'], user['paypal_account']), reply_markup=keyboard)

@bot.message_handler(commands=['searchorders'])
def search_order(message, value=-1):
	userId = message.chat.id
	
	if value == -1:
		msg = bot.send_message(userId, messages.search_order.text[0])
		collection.update_one({'_id': userId}, {'$set': {'function_name': 'process_search_order_step', 'use_function': True}})
		# bot.register_next_step_handler(msg, process_search_order_step)
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
		bot.send_message(userId, 'Invalid token', reply_markup=keyboard)
		return

	gig = getFromArrDict(user['gigs'], 'token', token)

	collection.update_one({'_id': userId}, {'$set': {'path': 'menu/profile_buyer/search_order?{}'.format(token)}})

	keyboard = create_keyboard(messages.search_order.buttons, [ [[''], [token]], [[''], [user['_id']]], empty_key])
	bot.send_message(userId, messages.search_order.text[1].format(gig['title'], gig['desc'], gig['price'], user['username']), reply_markup=keyboard)


def create_offer(message, value):
	userId = message.chat.id
	seller = collection.find_one({'gigs.token': value[0]})

	if seller['_id'] == userId:
		bot.send_message(userId, messages.create_offer.text[0])
		back(message)
		return

	gig = getFromArrDict(seller['gigs'], 'token', value[0])

	buyer = collection.find_one({'_id': userId})
	path = buyer['path']
	collection.update_one({'_id': userId}, {'$set': {'path': previous(path), 'process_order.token': value[0], 'process_order.customer': userId}})

	keyboard = create_keyboard(messages.create_offer.buttons, [empty_key, empty_key])
	bot.send_message(userId, messages.create_offer.text[1].format(gig['title'], gig['desc'], gig['price'], seller['username']), reply_markup=keyboard)
def create_offer_complete(message):
	userId = message.chat.id

	buyer = collection.find_one({'_id': userId})
	offer = buyer['process_order']
	seller = collection.find_one({'gigs.token': offer['token']})
	print(offer)
	print(seller, buyer)
	collection.update_one({'_id': seller['_id']}, {'$push': {'offers': offer}}) # Send offer to seller
	collection.update_one({'_id': userId}, {'$set': {'process_order': {'id': str(newId()), 'token': '#'}}}) # Clear process order of buyer

	bot.send_message(userId, messages.create_offer.text[2].format(seller['username']))
	bot.send_message(seller['_id'], messages.create_offer.text[3].format(buyer['username']))

def see_profile(message, value):
	userId = message.chat.id
	user = collection.find_one({'_id': int(value[0])})

	keyboard = create_keyboard(messages.see_profile.buttons, [empty_key])
	bot.send_message(userId, messages.see_profile.text.format(user['username'], user['name'], user['paypal_account']), reply_markup=keyboard)

####### SELLERS SYSTEM ########
def profile_seller(message):
	userId = message.chat.id
	user = collection.find_one({'_id': userId})
	keyboard = create_keyboard(messages.profile_seller.buttons, [empty_key, empty_key, empty_key, empty_key, empty_key])
	bot.send_message(userId, messages.profile_seller.text.format(user['name'], user['paypal_account']), reply_markup=keyboard)

@bot.message_handler(commands=['orders'])
def orders(message, value):
	userId = message.chat.id
	try:	
		orders = collection.find_one({'_id': userId})['{}_orders'.format(value[1])]
		if len(orders) == 0:
			bot.send_message(userId, messages.orders.text[0])
			back(message)
			return
	except:
		bot.send_message(userId, messages.orders.text[0])
		back(message)
		return

	value[0] = int(value[0])
	order = orders[value[0]]

	vals = [[[''], [max(value[0] - 1, 0), value[1]]], 
			[[''], [min(value[0] + 1, len(orders) - 1), value[1]]], 
			[[''], [order['seller_id']], {'show': '1' if value[1] == 'buyer' else '2'}], 
			[[''], [order['id']], {'show': '1' if value[1] == 'buyer' and order['status'] == 'pending' else '2'}],
			[[''], [order['id']], {'show': '1' if value[1] == 'buyer' and order['status'] == 'on hold' else '2'}],
			[[''], [order['id']], {'show': '1' if value[1] == 'seller' and order['status'] != 'complete' else '2'}], 
			empty_key]
	keyboard = create_keyboard(messages.orders.buttons, vals)

	if order['status'] == 'complete':
		ctime = 'FINSIHED'
	else:
		timeLeft = orders[value[0]]['end_date'] - time.time()
		if timeLeft >= 0:
			ctime = formatTime(time.gmtime(timeLeft))
		else:
			ctime = "LATE"
	bot.send_message(userId, messages.orders.text[1].format(orders[value[0]]['status'], orders[value[0]]['title'], orders[value[0]]['desc'], orders[value[0]]['price'], ctime), reply_markup=keyboard)
def deliver_order(message, value):
	seller = collection.find_one({'seller_orders.id': value[0]})
	
	order = getFromArrDict(seller['seller_orders'], 'id', value[0])

	buyer = collection.find_one({'_id': order['buyer_id']})
	collection.update_one({'seller_orders.id': value[0]}, {'$set': {'seller_orders.$.status': 'pending'}})
	collection.update_one({'buyer_orders.id': value[0]}, {'$set': {'buyer_orders.$.status': 'pending'}})

	keyboard = create_keyboard(messages.deliver_order.buttons, [[[''],[value[0]]], [[''],[value[0]]]])
	bot.send_message(order['buyer_id'], messages.deliver_order.text[0].format(value[0], seller['username']), reply_markup=keyboard)
	bot.send_message(order['seller_id'], messages.deliver_order.text[1].format(buyer['username']))
def deliver_order_complete(message, value):
	userId = message.chat.id
	seller = collection.find_one({'seller_orders.id': value[0]})
	
	order = getFromArrDict(seller['seller_orders'], 'id', value[0])

	buyer = collection.find_one({'_id': order['buyer_id']})

	sender_batch_id = newId()
	payout = Payout({
	    "sender_batch_header": {
	        "sender_batch_id": sender_batch_id,
	        "email_subject": "Order was completed"
	    },
	    "items": [
	        {
	            "recipient_type": "EMAIL",
	            "amount": {
	                "value": int(order['price']) * 0.9, # 10% of the order is left in admins account
	                "currency": CURRENCY
	            },
	            "receiver": seller['paypal_account'],
	            "note": "Thank you.",
	            "sender_item_id": "item_1"
	        }
	    ]
	})
	if payout.create():
		collection.update_one({'seller_orders.id': value[0]}, {'$set': {'seller_orders.$.status': 'complete'}})
		collection.update_one({'_id': userId, 'buyer_orders.id': value[0]}, {'$set': {'buyer_orders.$.status': 'complete'}})
		
		bot.send_message(buyer['_id'], messages.deliver_order.text[2].buyer[0])
		bot.send_message(seller['_id'], messages.deliver_order.text[3].seller[0])

		print("payout[%s] created successfully" % (payout.batch_header.payout_batch_id))
	else:
		bot.send_message(buyer['_id'], messages.deliver_order.text[2].buyer[1])
		bot.send_message(seller['_id'], messages.deliver_order.text[3].seller[1])
		print(payout.error)

def file_dispute(message, value):
	userId = message.chat.id
	msg = bot.send_message(userId, messages.file_dispute.text.buyer[0])
	collection.update_one({'_id': userId}, {'$set': {'function_name': 'file_dispute_complete', 'use_function': True}})
	# bot.register_next_step_handler(msg, file_dispute_complete)
def file_dispute_complete(message):
	text = message.text
	userId = message.chat.id

	buyer = collection.find_one({'_id': userId})
	print(buyer['path'])
	[query, value] = calc(re.search(r'\w+(|\?[^\/]+)$', buyer['path'])[0])

	print(query, value, buyer['path'], 'buyer')
	seller = collection.find_one({'seller_orders.id': value[0]})
	order = getFromArrDict(seller['seller_orders'], 'id', value[0])

	bot.send_message(seller['_id'], messages.file_dispute.text.seller[0].format(buyer['username']))
	bot.send_message(seller['_id'], messages.file_dispute.text.buyer[2].format(text))
	bot.send_message(userId, messages.file_dispute.text.buyer[1].format(seller['username']))

	collection.update_one({'seller_orders.id': value[0]}, {'$set': {'seller_orders.$.status': 'on hold'}})
	collection.update_one({'_id': userId, 'buyer_orders.id': value[0]}, {'$set': {'buyer_orders.$.status': 'on hold', 'function_name': 'file_dispute_complete', 'use_function': True}})

	collection_dispute.insert_one(order)
def close_dispute(message, value):
	userId = message.chat.id

	buyer = collection.find_one({'_id': userId})

	print(value, buyer['path'], 'buyer')
	seller = collection.find_one({'seller_orders.id': value[0]})
	order = getFromArrDict(seller['seller_orders'], 'id', value[0])

	bot.send_message(seller['_id'], messages.close_dispute.text.seller[0].format(buyer['username'], value[0]))
	bot.send_message(userId, messages.close_dispute.text.buyer[0].format(value[0]))

	collection.update_one({'seller_orders.id': value[0]}, {'$set': {'seller_orders.$.status': 'pending'}})
	collection.update_one({'_id': userId, 'buyer_orders.id': value[0]}, {'$set': {'buyer_orders.$.status': 'pending'}})

	collection_dispute.delete_one(order)

@bot.message_handler(commands=['offers'])
def offers(message, value=['0']):
	userId = message.chat.id
	try:	
		offers = collection.find_one({'_id': userId})['offers']
		if len(offers) == 0:
			bot.send_message(userId, messages.offers.text[1])
			back(message)
			return
	except:
		bot.send_message(userId, messages.offers.text[1])
		back(message)
		return
	value[0] = int(value[0])
	if value[0] - 1 < 0 or value[0] + 1 > len(offers) - 1:
		value[0] = 0

	vals = [ [[''], [max(value[0] - 1, 0)]], [[''], [min(value[0] + 1, len(offers) - 1)]], [[''], [offers[value[0]]['id']]], [[''], [offers[value[0]]['id']]], empty_key]
	keyboard = create_keyboard(messages.offers.buttons, vals)

	token = offers[value[0]]['token']
	gig = getFromArrDict(collection.find_one({'gigs.token': token})['gigs'], 'token', token)

	bot.send_message(userId, messages.offers.text[0].format(gig['title'], gig['desc'], gig['price']), reply_markup=keyboard)
def accept_offer(message, value):
	userId = message.chat.id

	seller = collection.find_one({'_id': userId})
	offer = getFromArrDict(seller['offers'], 'id', value[0])
	gig = getFromArrDict(seller['gigs'], 'token', offer['token'])
	buyer = collection.find_one({'_id': offer['customer']})

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
							'currency': CURRENCY,
							'quantity': 1
						}
					]
				},
				'amount': {
					'total': '{}.00'.format(gig['price']),
					'currency': CURRENCY
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
				bot.send_message(userId, messages.offers.text[2].format(buyer['username']))
				bot.send_message(offer['customer'], messages.offers.text[3].format(offer['id'], approval_url))
	else:
		bot.send_message(userId, messages.offers.text[4])

def decline_offer(message, value):
	userId = message.chat.id

	bot.send_message(userId, messages.offers.text[5])
	back(message)

	seller = collection.find_one({'_id': userId})
	offer = getFromArrDict(seller['offers'], 'id', value[0])


	collection.update_one({'_id': userId}, {'$pull': {'offers': {'id': offer['id']}}})
	bot.send_message(offer['customer'], messages.offers.text[6].format(seller['username']))

## CREATE NEW GIG SYSTEM ##
@bot.message_handler(commands=['createnewgig'])
def create_new_gig(message):
	userId = message.chat.id
	bot.send_message(userId, messages.create_new_gig.text[0])
	msg = bot.send_message(userId, messages.create_new_gig.text[1])
	collection.update_one({'_id': userId}, {'$set': {'function_name': 'process_create_new_gig_step_title', 'use_function': True}})
	# bot.register_next_step_handler(msg, process_create_new_gig_step_title)
def process_create_new_gig_step_title(message):
	userId = message.chat.id
	collection.update_one({'_id': userId}, {'$set': {'process_gig.title': message.text}})
	msg = bot.send_message(userId, messages.create_new_gig.text[2])
	collection.update_one({'_id': userId}, {'$set': {'function_name': 'process_create_new_gig_step_desc', 'use_function': True}})
	# bot.register_next_step_handler(msg, process_create_new_gig_step_desc)
def process_create_new_gig_step_desc(message):
	userId = message.chat.id
	collection.update_one({'_id': userId}, {'$set': {'process_gig.desc': message.text, 'function_name': 'process_create_new_gig_step_price', 'use_function': True}})
	msg = bot.send_message(userId, messages.create_new_gig.text[3])
	# bot.register_next_step_handler(msg, process_create_new_gig_step_price)
def process_create_new_gig_step_price(message):
	userId = message.chat.id
	if not RepresentsInt(message.text):
		msg = bot.send_message(userId, messages.create_new_gig.text[5])
		collection.update_one({'_id': userId}, {'$set': {'function_name': 'process_create_new_gig_step_price', 'use_function': True}})
		# bot.register_next_step_handler(msg, process_create_new_gig_step_price)
		return
	collection.update_one({'_id': userId}, {'$set': {'process_gig.price': message.text}})

	gig = collection.find_one({'_id': userId})['process_gig']
	bot.send_message(userId, messages.create_new_gig.text[4].format(gig['title'], gig['desc'], gig['price']))

	keyboard = create_keyboard(messages.create_new_gig.buttons, [empty_key, empty_key])
	bot.send_message(userId, messages.create_new_gig.text[6], reply_markup=keyboard)
def create_new_gig_complete(message):
	userId = message.chat.id

	gig = collection.find_one({'_id': userId})['process_gig']
	gig['token'] = newId()
	collection.update_one({'_id': userId}, {'$push': {'gigs': gig}, '$set': {'function_name': '', 'use_function': False}})

	# clear process_gig and change path
	bot.send_message(userId, messages.create_new_gig.text[7].format(gig['token']), parse_mode='html')
	bot.send_message(userId, messages.create_new_gig.text[8])

## REGISTERATION SYSTEM ##
@bot.message_handler(commands=['editprofile'])
def register(message):
	userId = message.chat.id
	bot.send_message(userId, messages.register.text[0])
	msg = bot.send_message(userId, messages.register.text[1])
	collection.update_one({'_id': userId}, {'$set': {'function_name': 'process_register_step_get_name', 'use_function': True}})
	# bot.register_next_step_handler(msg, process_register_step_get_name)
def process_register_step_get_name(message):
	userId = message.chat.id
	collection.update_one({'_id': userId}, {'$set': {'name': message.text, 'function_name': 'register_last_step', 'use_function': True}})
	msg = bot.send_message(userId, messages.register.text[2])
	# bot.register_next_step_handler(msg, register_last_step)
def register_last_step(message):
	userId = message.chat.id
	collection.update_one({'_id': userId}, {'$set': {'paypal_account': message.text}})

	user = collection.find_one({'_id': userId})
	bot.send_message(userId, messages.register.text[3].format(user['name'], user['paypal_account']))

	keyboard = create_keyboard(messages.register.buttons, [empty_key, empty_key])
	bot.send_message(userId, messages.register.text[4], reply_markup=keyboard)
def register_complete(message):
	userId = message.chat.id
	collection.update_one({'_id': userId}, {'$set': {
		'path': 'menu',
		'username': message.chat.username,
		'registered': True,
		'function_name': '', 
		'use_function': False}}) # set profile description
	bot.send_message(userId, messages.register.text[5])
	menu(message)

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

@bot.message_handler(func=lambda m: True)
def receiver(message):
	userId = message.chat.id
	user = collection.find_one({'_id': userId})
	if user['use_function']:
		possibles = globals().copy()
		possibles.update(locals())
		method = possibles.get(user['function_name'])
		method(message)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
	bot.delete_message(call.message.chat.id, call.message.message_id)

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