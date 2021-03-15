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