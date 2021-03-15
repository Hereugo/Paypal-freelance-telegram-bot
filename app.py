import re
import os
import time
from random import *
import string

# Telebot
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Paypal REST SDK
import paypalrestsdk
from paypalrestsdk import Payment, Payout

# Flask and Flask_Pymongo
from flask import Flask, jsonify, request
from flask_pymongo import PyMongo


from functions import *
from helpful_functions import *
from config import *
from setup import *

from bot import *
from buyer import *
from seller import *
from register import *


@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
	bot.enable_save_next_step_handlers(delay=3)
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
			'duration': int(offer['duration']),
			'start_time': t,
			'end_date': t + toSeconds(int(offer['duration']))
		})

		print(order)
		collection.update_one({'_id': uid1}, {'$push': {'seller_orders': order}, '$pull': {'offers': {'id': offer['id']}}})
		collection.update_one({'_id': uid2}, {'$push': {'buyer_orders': order}})
	else:
		print(payment.error)
		msg = bot.send_message(uid2, messages.payment_execute.text.buyer[0])
	menu(msg)

	return "Payment success!", 200

@app.route('/')
def webhook():
	bot.remove_webhook()
	bot.set_webhook(url=URL + TOKEN)
	return '!', 200

if __name__ == "__main__":
	app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))