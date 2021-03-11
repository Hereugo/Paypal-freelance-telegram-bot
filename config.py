from functions import Map

TOKEN = "1272925344:AAFO3V-DSpEcMYkfL8oMZ38Ei7JlAFIXr-o"
URI = 'mongodb+srv://Amir:2LSCfSNcwAz9x3!@cluster0.jxsw1.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
URL = 'https://paypal-telegram-fiverr-bot.herokuapp.com/'
CLIENT_ID = "AW7Q6ChzzOnd5wa8OuYbiP5RiaqQ6tumVR7UTlMLaDIF_FXRhxo77BaNmjgQfKN6GBLK5c2rDHiijpHv"
CLIENT_SECRET = "EBBmQczfJM6WrweaUE-NDMOxpBn__GH_RXtXQB1nwt8AN6doaa7MBEYuf3ok6EREj8AsrL7Eg7vSE4wM"
CURRENCY = "USD"

# PATH SYSTEM

messages = Map({
	'menu': {
		'text': "Welcome!",
		'buttons': [
			[
				{
					'text': 'As seller',
					'callback_data': 'profile_seller',
				},
				{
					'text': 'As buyer',
					'callback_data': 'profile_buyer',
				}
			]
		]
	},
	'profile_buyer': {
		'text': "Name {}\nPaypal: {}\n",
		'buttons': [
			[
				{
					'text': 'Orders',
					'callback_data': 'orders?0,buyer',
				},
				{
					'text': 'Search order',
					'callback_data': 'search_order',
				}
			],
			[
				{
					'text': 'Back',
					'callback_data': 'back',
				}
			]
		],
	},
	'search_order': {
		'text': "{}\n\n{}\n\nPrice: {} "+CURRENCY+"\n\nUser: {}",
		'buttons': [
			[
				{
					'text': 'Create an offer',
					'callback_data': 'create_offer?{},9',
				}
			],
			[
				{
					'text': 'See Profile',
					'callback_data': 'see_profile?{}',
				}
			],
			[
				{
					'text': 'Back',
					'callback_data': 'back',
				}
			]
		],
	},
	'create_offer': {
		'text': '{}\n\n{}\n\nPrice: {} '+CURRENCY+'\n\nUser: {}\nDuration: {} days',
		'buttons': [
			[	
				{
					'text': 'Set time',
					'callback_data': 'create_offer?{},{}',
				},
			],
			[
				{
					'text': 'Send',
					'callback_data': 'create_offer_complete'
				},
			],
			[
				{
					'text': 'Back',
					'callback_data': 'back',
				}
			]
		],
	},
	'create_offer_complete': {
		'text': ['Offer has been sent, wait for a seller to confirm', 'New offer from {}'],
	},
	'see_profile': {
		'text': 'Name: {}\n\n{}',
		'buttons': [
			[
				{
					'text': 'Start a conversation',
					'callback_data': 'start_conversation?{}',
				},
			],
			[
				{
					'text': 'More Services',
					'callback_data': 'gigs?0,0',
				},
			],
			[
				{
					'text': 'Back',
					'callback_data': 'back',
				}
			]
		],
	},
	'start_conversation': {
		'text': '@{}',
		'buttons': [
			[
				{
					'text': 'Back',
					'callback_data': 'back',
				}
			]
		],
	},
	'profile_seller': {
		'text': "Name: {}\nPaypal: {}\n\n{}",
		'buttons': [
			[
				{
					'text': 'Orders',
					'callback_data': 'orders?0,seller',
				},
				{
					'text': 'Offers',
					'callback_data': 'offers?0',
				}
			],
			[
				{
					'text': 'Gigs',
					'callback_data': 'gigs?0,1',
				},
				{
					'text': 'Create new gig',
					'callback_data': 'create_new_gig?9',
				}
			],
			[
				{
					'text': 'Edit profile',
					'callback_data': 'register?9'
				}
			],
			[
				{
					'text': 'Back',
					'callback_data': 'back',
				}
			]
		],
	},
	'orders': {
		'text': 'Project status: {}\n\nTitle: {}\n {}\n\n Price: {} '+CURRENCY+'\n Duration: {} days\n Time left: {}',
		'buttons': [
			[
				{
					'text': '<',
					'callback_data': 'orders?{},{}',
				},
				{
					'text': '>',
					'callback_data': 'orders?{},{}',
				}
			],
			[
				{
					'text': 'Start a conversation',
					'callback_data': 'start_conversation?{}',
				}
			],
			[
				{
					'text': 'File a dispute',
					'callback_data': 'file_dispute?{}',
				}
			],
			[
				{
					'text': 'deliver order',
					'callback_data': 'deliver_order?{}',
				}
			],
			[
				{
					'text': 'Back',
					'callback_data': 'back',
				}
			]
		],
	},
	'deliver_order': {
		'text': ['Order {} was completed by {}, mark it complete to finish the order', 'Wait for {} to mark your order complete or decline'],
		'buttons': [
			[
				{
					'text': 'Complete',
					'callback_data': 'deliver_order_complete?{}',
				}
			],
			[
				{
					'text': 'Decline',
					'callback_data': 'deliver_order_decline?{}',
				}
			]
		]
	},
	'offers': {
		'text': 'Title: {}\n {}\n\n Price: {} '+CURRENCY+'\n Duration: {} days',
		'buttons': [
			[
				{
					'text': '<',
					'callback_data': 'offers?{}',
				},
				{
					'text': '>',
					'callback_data': 'offers?{}',
				}
			],
			[
				{
					'text': 'Accept',
					'callback_data': 'accept_offer?{}',
				},
				{
					'text': 'Decline',
					'callback_data': 'decline_offer?{}',
				}
			],
			[
				{
					'text': 'Back',
					'callback_data': 'back',
				}
			]
		],
	},
	'gigs': {
		'text': 'Title: {}\n\nDescription: {}\n\n Price: {} '+CURRENCY,
		'buttons': [
			[
				{
					'text': '<',
					'callback_data': 'gigs?{},{}',
				},
				{
					'text': '>',
					'callback_data': 'gigs?{},{}',
				}
			],
			[
				{
					'show': True,
					'text': 'Edit gig',
					'callback_data': 'edit_gig?9,{}',
				}
			],
			[
				{
					'text': 'Recieve token of this gig',
					'callback_data': 'token_reciever?{}',
				}
			],
			[
				{
					'text': 'Back',
					'callback_data': 'back',
				}
			]
		],
	},
	'token_reciever': {
		'text': '{}',
		'buttons': [
			[
				{
					'text': 'Back',
					'callback_data': 'back',
				}
			]
		],
	},
	'create_new_gig': {
		'text': 'Title:{}\n\nDescription:{}\n\n Price:{} '+CURRENCY,
		'buttons': [
			[
				{
					'text': 'Title',
					'callback_data': 'create_new_gig?0',
				},
				{
					'text': 'Price',
					'callback_data': 'create_new_gig?2',
				}
			],
			[
				{
					'text': 'Description',
					'callback_data': 'create_new_gig?1',
				}
			],
			[
				{
					'text': 'Save',
					'callback_data': 'create_new_gig_complete',
				}
			],
			[
				{
					'text': 'Delete gig',
					'callback_data': 'delete_gig?{}'
				}
			],
			[
				{
					'text': 'Back',
					'callback_data': 'back',
				}
			]
		],
	},
	'delete_gig': {
		'text': 'Gig has been deleted'
	},
	'register': {
		'text': "Name: {}\nPaypal: {} "+CURRENCY+"\n\nDescription: {}",
		'buttons': [
			[
				{
					'text': 'Name',
					'callback_data': 'register?0',
				},
				{
					'text': 'Paypal',
					'callback_data': 'register?1',
				}
			],
			[
				{
					'text': 'Description',
					'callback_data': 'register?2',
				}
			],
			[
				{
					'text': 'Save',
					'callback_data': 'register_complete',
				}
			],
			[
				{
					'text': 'Back',
					'callback_data': 'back',
				}
			],
		],
	}
});
