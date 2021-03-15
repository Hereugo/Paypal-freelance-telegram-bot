def getFromArrDict(arr, name, val):
	for x in arr:
		if x[name] == val:
			return x
	return None

def formatTime(x):
	return '{} days {} hours {} minutes {} seconds'.format(x.tm_mday, x.tm_hour, x.tm_min, x.tm_sec) 

def toSeconds(x):
	return x * 24 * 60 * 60

def newId():
	return ''.join(random.choice(string.ascii_uppercase) for i in range(12))

def previous(path):
	return re.search(r'(.+\/)+', path)[0][:-1]

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
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