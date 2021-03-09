from functions import Map

TOKEN = "1272925344:AAFO3V-DSpEcMYkfL8oMZ38Ei7JlAFIXr-o"

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
			],
		]
	},
	'profile_buyer': {
		'text': "Name {}\nPaypal: {}\n",
		'buttons': [
			[
				{
					'text':'Active Orders',
					'callback_data': 'active_orders',
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
		'text': "{}\n\n{}\n\nPrice: {}\n\nUser: {}",
		'buttons': [
			{
				'text': 'Create an offer',
				'callback_data': 'create_offer?{},9',
			},
			{
				'text': 'See Profile',
				'callback_data': 'see_profile?{}',
			},
			{
				'text': 'Back',
				'callback_data': 'back',
			}
		],
	},
	'create_offer': {
		'text': '{}\n\n{}\n\nPrice: {}\n\nUser: {}\nTime: {} days',
		'buttons': [
			{
				'text': 'Set time',
				'callback_data': 'create_offer?{},{}',
			},
			{
				'text': 'Send',
				'callback_data': 'create_offer_complete'
			},
			{
				'text': 'Back',
				'callback_data': 'back',
			}
		],
	},
	'create_offer_complete': {
		'text': ['Offer has been sent, wait for a seller to confirm', 'New offer from {}'],
	},
	'see_profile': {
		'text': 'Name: {}\n\n{}',
		'buttons': [
			{
				'text': 'Start a conversation',
				'callback_data': 'start_conversation?{}',
			},
			{
				'text': 'More Services',
				'callback_data': 'gigs?0,0',
			},
			{
				'text': 'Back',
				'callback_data': 'back',
			}
		],
	},
	'start_conversation': {
		'text': '@{}',
		'buttons': [
			{
				'text': 'Back',
				'callback_data': 'back',
			}
		],
	},
	'profile_seller': {
		'text': "Name: {}\nPaypal: {}\n\n{}",
		'buttons': [
			{
				'text': 'Active orders',
				'callback_data': 'orders?0',
			},
			{
				'text': 'Offers',
				'callback_data': 'offers?0',
			},
			{
				'text': 'Gigs',
				'callback_data': 'gigs?0,1',
			},
			{
				'text': 'Create new gig',
				'callback_data': 'create_new_gig?9',
			},
			{
				'text': 'Edit profile',
				'callback_data': 'register?9'
			},
			{
				'text': 'Back',
				'callback_data': 'back',
			},
		],
	},
	'orders': {
		'text': 'Title: {}\n {}\n\n Price: {}\n Duration: {} days\n Time left: {}',
		'buttons': [
			{
				'text': '<',
				'callback_data': 'orders?{}',
			},
			{
				'text': '>',
				'callback_data': 'orders?{}',
			},
			{
				'text': 'deliver order',
				'callback_data': 'deliver_order',
			},
			{
				'text': 'Back',
				'callback_data': 'back',
			}
		]
	},
	'offers': {
		'text': 'Title: {}\n {}\n\n Price: {}\n Duration: {} days',
		'buttons': [
			{
				'text': '<',
				'callback_data': 'offers?{}',
			},
			{
				'text': '>',
				'callback_data': 'offers?{}',
			},
			{
				'text': 'Accept',
				'callback_data': 'accept_offer?{}',
			},
			{
				'text': 'Decline',
				'callback_data': 'decline_offer?{}',
			},
			{
				'text': 'Back',
				'callback_data': 'back',
			}
		],
	},
	'gigs': {
		'text': 'Title: {}\n\nDescription: {}\n\n Price: {}',
		'buttons': [
			{
				'text': '<',
				'callback_data': 'gigs?{},{}',
			},
			{
				'show': True,
				'text': 'Edit gig',
				'callback_data': 'edit_gig?9,{}',
			},
			{
				'text': '>',
				'callback_data': 'gigs?{},{}',
			},
			{
				'text': 'Recieve token of this gig',
				'callback_data': 'token_reciever?{}',
			},
			{
				'text': 'Back',
				'callback_data': 'back',
			}
		],
	},
	'token_reciever': {
		'text': '{}',
		'buttons': [
			{
				'text': 'Back',
				'callback_data': 'back',
			}
		],
	},
	'create_new_gig': {
		'text': 'Title:{}\n\nDescription:{}\n\n Price:{}',
		'buttons': [
			{
				'text': 'Title',
				'callback_data': 'create_new_gig?0',
			},
			{
				'text': 'Description',
				'callback_data': 'create_new_gig?1',
			},
			{
				'text': 'Price',
				'callback_data': 'create_new_gig?2',
			},
			{
				'text': 'Save',
				'callback_data': 'create_new_gig_complete',
			},
			{
				'text': 'Back',
				'callback_data': 'back',
			}
		],
	},
	'register': {
		'text': "Name: {}\nPaypal: {}\n\nDescription: {}",
		'buttons': [
			{
				'text': 'Name',
				'callback_data': 'register?0',
			},
			{
				'text': 'Paypal',
				'callback_data': 'register?1',
			},
			{
				'text': 'Description',
				'callback_data': 'register?2',
			},
			{
				'text': 'Save',
				'callback_data': 'register_complete',
			},
			{
				'text': 'Back',
				'callback_data': 'back',
			}
		],
	}
});
