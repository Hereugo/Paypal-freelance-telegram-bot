from functions import Map

token = "1272925344:AAFO3V-DSpEcMYkfL8oMZ38Ei7JlAFIXr-o"

# PATH SYSTEM

messages = Map({
	'menu': {
		'text': "Welcome!",
		'buttons': [
			{
				'text': 'As seller',
				'callback_data': 'profile_seller',
			},
			{
				'text': 'As buyer',
				'callback_data': 'profile_buyer',
			}
		],
	},
	'profile_buyer': {
		'text': "Name {}\nPaypal: {}\n",
		'buttons': [
			{
				'text':'Active Orders',
				'callback_data': 'active_orders',
			},
			{
				'text': 'Search order',
				'callback_data': 'search_order',
			},
			{
				'text': 'Back',
				'callback_data': 'back',
			}
		],
	},
	'search_order': {
		'text': "{}\n\n{}\n\nPrice: {}\n\nUser: {}",
		'buttons': [
			{
				'text': 'Buy order',
				'callback_data': 'buy_order?{}',
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
				'text': 'Orders',
				'callback_data': 'orders',
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

	},
	'gigs': {
		'text': 'Title:{}\n\nDescription:{}\n\n Price:{}',
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
