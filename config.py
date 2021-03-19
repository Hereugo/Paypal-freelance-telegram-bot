from functions import Map

TOKEN = "1272925344:AAFO3V-DSpEcMYkfL8oMZ38Ei7JlAFIXr-o"
URI = 'mongodb+srv://Amir:2LSCfSNcwAz9x3!@cluster0.jxsw1.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
URL = 'https://paypal-telegram-fiverr-bot.herokuapp.com/' # Don't forget to add '/'' at the end your URL 
CLIENT_ID = "AW7Q6ChzzOnd5wa8OuYbiP5RiaqQ6tumVR7UTlMLaDIF_FXRhxo77BaNmjgQfKN6GBLK5c2rDHiijpHv"
CLIENT_SECRET = "EBBmQczfJM6WrweaUE-NDMOxpBn__GH_RXtXQB1nwt8AN6doaa7MBEYuf3ok6EREj8AsrL7Eg7vSE4wM"
CURRENCY = "ILS"


TEMPLATE_MESSAGE = ("I'm the bot for create and manage your gigs, you can control me by sending those commends:\n"
					"/start - start the bot\n"
					"/createnewgig - Create new gig\n"
					"/editprofile - Edit your profile\n"
					"/orders - See all your orders\n"
					"/offers - See all your offers\n"
					"/searchorder - Search order\n"
					"/back - go back to previous message\n")

# PATH SYSTEM
messages = Map({
	'payment_execute': {
		'text': {
			'buyer': ['Payment was successful\n Order has been started!',
					  'Something went wrong, try again later'],
			'seller': ['Order has been started!'],
		} 		 
	},
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
		'text': "PROFILE\n\nName: {}\nPaypal: {}\n",
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
		'text': ["Please send a given token here",
				 "{}\n\n{}\n\nPrice: {} "+CURRENCY+"\n\nUser: @{}"],
		'buttons': [
			[
				{
					'text': 'Create an offer',
					'callback_data': 'create_offer?{}',
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
		'text': ['Cant make an offer to yourself',
				 '{}\n\n{}\n\nPrice: {} '+CURRENCY+'\n\nUser: @{}\nDuration: 2 days',
				 'Offer has been sent, wait for a seller @{} to confirm',
				 'New offer from @{}',
				 'Something went wrong'],
		'buttons': [
			[
				{
					'text': 'Send',
					'callback_data': 'create_offer_complete',
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
	'see_profile': {
		'text': 'PROFILE OF @{}\n\nName: {}\nPaypal: {}',
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
		'text': "PROFILE\n\nName: {}\nPaypal: {}",
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
					'text': 'Create new gig',
					'callback_data': 'create_new_gig',
				}
			],
			[
				{
					'text': 'Edit profile',
					'callback_data': 'register'
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
		'text': ['No current orders',
				 'Project status: {}\n\nTitle: {}\n\n {}\n\n Price: {} '+CURRENCY+'\n Time left: {}'],
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
					'text': 'Close a dispute',
					'callback_data': 'close_dispute?{}',
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
	'file_dispute': {
		'text': {
			'buyer': ['Please tell us what is your problem..',
					  'Dispute was send to the seller @{}',
					  'Dispute reason: {}'],
			'seller': ['@{} buyer has disputed the order, responed to the buyer in 24 hours'],
		}
	},
	'close_dispute': {
		'text': {
			'buyer': ['Dispute for order {} is closed'],
			'seller': ['Buyer @{} closed the dispute for order {}'],
		}
	},
	'deliver_order': {
		'text': ['Order {} was completed by @{}, You have 10 hours to mark it complete to finish the order, or else the order will be automatically be marked completed', 
				 'Wait for @{} to mark your order complete or decline',
				 {
				 	'buyer': ['Thank you for using our services!',
				 			  'Something went wrong, please continue when seller has fixed his issue',
				 			  'Delivery declined']
				 },
				 {
				 	'seller': ['Order was completed, payment was done through your paypal',
				 			   'Something went wrong, please check if your paypal account correctly written',
				 			   'Your delivery was declined']
				 }],
		'buttons': [
			[
				{
					'text': 'Complete',
					'callback_data': 'deliver_order_complete?{}',
				}
			],
			[
				{
					'text': 'File a dispute',
					'callback_data': 'file_dispute?{}',
				}
			]
		]
	},
	'offers': {
		'text': ['Title: {}\n {}\n\n Price: {} '+CURRENCY+'\n Duration: 2 days',
				 'No offers were found',
				 'OK, waiting for @{} to pay the money. After successful payment the order will start',
				 'Offer {} was accepted\n To begin this order pay using this link {}',
				 'Something went wrong',

				 'Offer was declined',
				 '{} has declined your offer'],
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
	'create_new_gig': {
		'text': ['Ok, lets create new gig',
				 'Please type the gig title',
				 'Please type the gig description',
				 'Please type the price for this gig',
				 'Ok, this is the info you type:\n\nTitle:{}\n\nDescription:{}\n\n Price:{} '+CURRENCY,
				 'Your price need only contains numbers! like this: 14 or 14.99. Please type again...',
				 'Is this info is correct?',
				 'Ok all good, your token for this gig is:',
				 '<code>{}</code>',
				 'Please give this token to the buyer. Please note that after the buyer accept your order you have 2 days to supply the gig.',
				 'Gig has been saved!'],
		'buttons': [
			[
				{
					'text': 'Yes',
					'callback_data': 'create_new_gig_complete',
				},
				{
					'text': 'No',
					'callback_data': 'create_new_gig'
				}
			]
		],
	},
	'register': {
		'text': ['Register lets add some info about you',
				 'Typin your name',
				 'Typin your paypal account',
				 'Ok, this is the info you type:\n\nName: {}\nPaypal: {}\n',
				 'Is this info is correct?',
				 'Registeration completed!'],
		'buttons': [
			[
				{
					'text': 'Yes',
					'callback_data': 'register_complete',
				},
				{
					'text': 'No',
					'callback_data': 'register',
				}
			],
		],
	}
});
