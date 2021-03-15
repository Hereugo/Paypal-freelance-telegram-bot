def checkRegistration(message, user):
	userId = message.chat.id
	if not user['registered']:
		collection.update_one({'_id': userId}, {'$set': {'path': 'menu/register'}})
		register(message)
		return True
	return False

def register(message):
	userId = message.chat.id
	bot.send_message(userId, messages.register.text[0])
	msg = bot.send_message(userId, messages.register.text[1])
	bot.register_next_step_handler(msg, process_register_step_get_name)

def process_register_step_get_name(message):
	userId = message.chat.id
	collection.update_one({'_id': userId}, {'$set': {'name': message.text}})
	msg = bot.send_message(userId, messages.register.text[2])
	bot.register_next_step_handler(msg, register_last_step)

def register_last_step(message):
	userId = message.chat.id
	collection.update_one({'_id': userId}, {'$set': {'paypal_account': message.text}})

	user = collection.find_one({'_id': userId})
	bot.send_message(userId, messages.register.text[3].format(user['name'], user['paypal_account']))

	keyboard = create_keyboard(messages.register.buttons, [empty_key, empty_key])
	bot.send_message(userId, messages.register.text[4], reply_markup=keyboard)

def register_complete(message):
	userId = message.chat.id
	collection.update_one({'_id': userId}, {'$set': {'path': 'menu','username': message.chat.username,'registered': True}}) # set profile description
	bot.send_message(userId, messages.register.text[5])
	menu(message)