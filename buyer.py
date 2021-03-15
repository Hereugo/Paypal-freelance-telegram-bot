def profile_buyer(message):
	userId = message.chat.id
	user = collection.find_one({'_id': userId})
	keyboard = create_keyboard(messages.profile_buyer.buttons, [empty_key, empty_key, empty_key])
	bot.send_message(userId, messages.profile_buyer.text.format(user['name'], user['paypal_account']), reply_markup=keyboard)

def search_order(message, value=-1):
	userId = message.chat.id
	
	if value == -1:
		keyboard = InlineKeyboardMarkup()
		keyboard.add(InlineKeyboardButton('Back', callback_data='back'))
		msg = bot.send_message(userId, messages.search_order.text[0], reply_markup=keyboard)
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

	gig = getFromArrDict(user['gigs'], 'token', token)

	collection.update_one({'_id': userId}, {'$set': {'path': 'menu/profile_buyer/search_order?{}'.format(token)}})

	keyboard = create_keyboard(messages.search_order.buttons, [ [[''], [token]], [[''], [user['_id']]], empty_key])
	bot.send_message(userId, messages.search_order.text[1].format(gig['title'], gig['desc'], gig['price'], user['username']), reply_markup=keyboard)


def create_offer(message):
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
	collection.update_one({'_id': userId}, {'$set': {'process_order': {'id': str(newId()), 'duration': "", 'token': '#'}}}) # Clear process order of buyer

	bot.send_message(userId, messages.create_offer.text[2].format(seller['username']))
	bot.send_message(seller['_id'], messages.create_offer.text[3].format(buyer['username']))

def see_profile(message, value):
	userId = message.chat.id
	user = collection.find_one({'_id': int(value[0])})

	keyboard = create_keyboard(messages.see_profile.buttons, [empty_key])
	bot.send_message(userId, messages.see_profile.text.format(user['username'], user['name'], user['paypal_account']), reply_markup=keyboard)

def file_dispute(message, value):
	userId = message.chat.id
	msg = bot.send_message(userId, messages.file_dispute.text.buyer[0])
	bot.register_next_step_handler(msg, file_dispute_complete)

def file_dispute_complete(message):
	text = message.text
	userId = message.chat.id

	buyer = collection.find_one({'_id': userId})
	[query, value] = calc(re.search(r'\w+(|\?[^\/]+)$', buyer['path'])[0])
	print(query, value, buyer['path'], 'buyer')
	seller = collection.find_one({'seller_orders.id': value[0]})
	order = getFromArrDict(seller['seller_orders'], 'id', value[0])

	bot.send_message(seller['_id'], messages.file_dispute.text.seller[0].format(buyer['username']))
	bot.send_message(seller['_id'], text)
	bot.send_message(userId, messages.file_dispute.text.buyer[1].format(seller['username']))

	collection.update_one({'seller_orders.id': value[0]}, {'$set': {'seller_orders.$.status': 'on hold'}})
	collection.update_one({'_id': userId, 'buyer_orders.id': value[0]}, {'$set': {'buyer_orders.$.status': 'on hold'}})

	collection_dispute.insert_one(order)