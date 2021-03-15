# Telebot
bot = telebot.TeleBot(TOKEN)

# Flask
app = Flask(__name__)
cluster = PyMongo(app, uri=URI)
collection = cluster.db.user
collection_dispute = cluster.db.dispute

empty_key = [[''], ['']]

# Paypal python sdk
paypalrestsdk.configure({
	"mode": "sandbox", # sandbox or live
	"client_id": CLIENT_ID,
	"client_secret": CLIENT_SECRET,
})