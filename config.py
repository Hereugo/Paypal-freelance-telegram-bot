from functions import Map

TOKEN = "1272925344:AAFO3V-DSpEcMYkfL8oMZ38Ei7JlAFIXr-o"
URI = 'mongodb+srv://Amir:2LSCfSNcwAz9x3!@cluster0.jxsw1.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
URL = 'https://paypal-telegram-fiverr-bot.herokuapp.com/'
CLIENT_ID = "AW7Q6ChzzOnd5wa8OuYbiP5RiaqQ6tumVR7UTlMLaDIF_FXRhxo77BaNmjgQfKN6GBLK5c2rDHiijpHv"
CLIENT_SECRET = "EBBmQczfJM6WrweaUE-NDMOxpBn__GH_RXtXQB1nwt8AN6doaa7MBEYuf3ok6EREj8AsrL7Eg7vSE4wM"
CURRENCY = "USD"

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
		'text': "PROFILE\n\nName {}\nPaypal: {}\n",
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
		'text': ['Cant make an offer to yourself',
				 '{}\n\n{}\n\nPrice: {} '+CURRENCY+'\n\nUser: @{}\nDuration: {} days',
				 'Offer has been sent, wait for a seller to confirm',
				 'New offer from @{}'],
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
				 'Project status: {}\n\nTitle: {}\n {}\n\n Price: {} '+CURRENCY+'\n Duration: {} days\n Time left: {}'],
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
	'file_dispute': {
		'text': {
			'buyer': ['Send what problem did your have',
					  'Dispute was send to the seller @{}'],
			'seller': ['@{} buyer has disputed the order, responed to the buyer in 24 hours',
					   ],
		}
	},
	'deliver_order': {
		'text': ['Order {} was completed by @{}, mark it complete to finish the order', 
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
					'text': 'Decline',
					'callback_data': 'deliver_order_decline?{}',
				}
			]
		]
	},
	'offers': {
		'text': ['Title: {}\n {}\n\n Price: {} '+CURRENCY+'\n Duration: {} days',
				 'No offers were found',
				 'Wait for an order to start',
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
	# 'gigs': {
	# 	'text': ['No gigs were made',
	# 			 'Title: {}\n\nDescription: {}\n\n Price: {} '+CURRENCY],
	# 	'buttons': [
	# 		[
	# 			{
	# 				'text': '<',
	# 				'callback_data': 'gigs?{},{}',
	# 			},
	# 			{
	# 				'text': '>',
	# 				'callback_data': 'gigs?{},{}',
	# 			}
	# 		],
	# 		[
	# 			{
	# 				'show': True,
	# 				'text': 'Edit gig',
	# 				'callback_data': 'edit_gig?9,{}',
	# 			}
	# 		],
	# 		[
	# 			{
	# 				'text': 'Recieve token of this gig',
	# 				'callback_data': 'token_reciever?{}',
	# 			}
	# 		],
	# 		[
	# 			{
	# 				'text': 'Back',
	# 				'callback_data': 'back',
	# 			}
	# 		]
	# 	],
	# },
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
		'text': ['Ok, lets create new gig',
				 'Please type the gig title',
				 'Please type the gig description',
				 'Please type the price for this gig',
				 'Ok, this is the info you type:\n\nTitle:{}\n\nDescription:{}\n\n Price:{} '+CURRENCY,
				 'Your price need only contains numbers! like this: 14. Please type again...',
				 'Is this info is correct?',
				 'Ok all good, your token for this gig is: {}\nPlease give this token to the buyer. Please note that after the buyer accept your order you have 2 days to supply the gig.',
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
	'delete_gig': {
		'text': 'Gig has been deleted'
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
