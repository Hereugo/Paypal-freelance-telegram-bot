def profile_seller(message):
	userId = message.chat.id
	user = collection.find_one({'_id': userId})
	keyboard = create_keyboard(messages.profile_seller.buttons, [empty_key, empty_key, empty_key, empty_key, empty_key])
	bot.send_message(userId, messages.profile_seller.text.format(user['name'], user['paypal_account']), reply_markup=keyboard)

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
	bot.send_message(userId, messages.orders.text[1].format(orders[value[0]]['status'], orders[value[0]]['title'], orders[value[0]]['desc'], orders[value[0]]['price'], orders[value[0]]['duration'], ctime), reply_markup=keyboard)

def deliver_order(message, value):
	seller = collection.find_one({'seller_orders.id': value[0]})
	
	order = getFromArrDict(seller['seller_orders'], 'id', value[0])

	buyer = collection.find_one({'_id': order['buyer_id']})
	collection.update_one({'seller_orders.id': value[0]}, {'$set': {'seller_orders.$.status': 'pending'}})
	collection.update_one({'buyer_orders.id': value[0]}, {'$set': {'buyer_orders.$.status': 'pending'}})

	keyboard = create_keyboard(messages.deliver_order.buttons, [[[''],[value[0]]], [[''],[value[0]]]])
	bot.send_message(order['buyer_id'], messages.deliver_order.text[0].format(value[0], seller['username']), reply_markup=keyboard)
	bot.send_message(order['seller_id'], messages.deliver_order.text[1].format(buyer['username']))
	menu(message)

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

def deliver_order_decline(message, value):
	userId = message.chat.id
	seller = collection.find_one({'seller_orders.id': value[0]})
	order = getFromArrDict(seller['seller_orders'], 'id', value[0])
	buyer = collection.find_one({'_id': order['buyer_id']})

	bot.send_message(buyer['_id'], messages.deliver_order.text[2].buyer[2])
	bot.send_message(seller['_id'], messages.deliver_order.text[3].seller[2])



def offers(message, value):
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

	bot.send_message(userId, messages.offers.text[0].format(gig['title'], gig['desc'], gig['price'], offers[value[0]]['duration']), reply_markup=keyboard)

def accept_offer(message, value):
	userId = message.chat.id

	bot.send_message(userId, messages.offers.text[2])
	menu(message)

	seller = collection.find_one({'_id': userId})
	offer = getFromArrDict(seller['offers'], 'id', value[0])
	gig = getFromArrDict(seller['gigs'], 'token', offer['token'])


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
def create_new_gig(message):
	userId = message.chat.id
	bot.send_message(userId, messages.create_new_gig.text[0])
	msg = bot.send_message(userId, messages.create_new_gig.text[1])
	bot.register_next_step_handler(msg, process_create_new_gig_step_title)
def process_create_new_gig_step_title(message):
	userId = message.chat.id
	collection.update_one({'_id': userId}, {'$set': {'process_gig.title': message.text}})
	msg = bot.send_message(userId, messages.create_new_gig.text[2])
	bot.register_next_step_handler(msg, process_create_new_gig_step_desc)
def process_create_new_gig_step_desc(message):
	userId = message.chat.id
	collection.update_one({'_id': userId}, {'$set': {'process_gig.desc': message.text}})
	msg = bot.send_message(userId, messages.create_new_gig.text[3])
	bot.register_next_step_handler(msg, process_create_new_gig_step_price)
def process_create_new_gig_step_price(message):
	userId = message.chat.id
	if not RepresentsInt(message.text):
		msg = bot.send_message(userId, messages.create_new_gig.text[5])
		bot.register_next_step_handler(msg, process_create_new_gig_step_price)
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
	collection.update_one({'_id': userId}, {'$push': {'gigs': gig}})

	# clear process_gig and change path
	bot.send_message(userId, messages.create_new_gig.text[7].format(gig['token']))
	bot.send_message(userId, messages.create_new_gig.text[8])

