from flask import Flask, jsonify, render_template, make_response, request, flash, redirect, url_for
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbSeed import Category, Item
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import requests
import random, string
import json

app = Flask(__name__)
app.debug = True

""" This key should normally be hard to guess, like a strong password. For now,
 we're going to use something simple. """
 
app.secret_key = 'super secret key'

engine = create_engine('sqlite:///catalog.db')
session = sessionmaker()
session.configure(bind=engine)
s = session()

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']

# Helper methods to improve code reuse

def getCategories():
	return s.query(Category).all()

def getSpecificCategory(categoryName):
	return s.query(Category).filter(Category.name == categoryName).first()
	
def getItem(ItemName):
	return s.query(Item).filter(Item.name == ItemName).first()

# This is one of the methods borrowed from ud330
def getRandomTokenString():
	print 'generating state'
	return ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))

def isUserLoggedIn():
	#Check if the user is logged in.  'username' should be in login_session if the user is logged in.
	if 'username' not in login_session:
		print 'user is not logged in'
		return False
	else:
		print 'user is logged in'
		return True

# Routes
#app.add_url_rule('/favicon.ico', redirect_to=url_for('static', filename='favicon.ico'))

@app.route('/')
def hello_world():
	categories = getCategories()
	login_session['state'] = getRandomTokenString()
			
	return render_template('index.html', categories = categories, loggedIn = isUserLoggedIn(), STATE = login_session['state'])
	
# This is another method borrowed from ud330, and remains mostly unchanged.
@app.route('/gconnect', methods=['POST'])
def gconnect():
	print request.args.get('state')
	print login_session['state']
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	
	code = request.data
	try:
		oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials= oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(json.dumps('Failed to upgrade the authorization code.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])
	
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		
	gplus_id = credentials.id_token['sub']
	
	if result['user_id'] != gplus_id:
		response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
		
	if result['issued_to'] != CLIENT_ID:
		response = make_response(json.dumps("Token's client ID does not match app's"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')

	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	login_session['credentials'] = credentials.access_token
	login_session['gplus_id'] = gplus_id
	
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)
	
	data = answer.json()
	
	login_session['username'] = data['name']
	login_session['email'] = data['email']
	
	response = make_response(json.dumps('Logged in!'), 200)
	response.headers['Content-Type'] = 'application/json'
	
	return response
	
# Here's another method borrowed from ud330, mostly unchanged.
@app.route('/gdisconnect')
def gdisconnect():
	# Only disconnect a connected user.
	
	credentials = login_session.get('credentials')
	if credentials is None:
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
		
	access_token = credentials
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	
	if result['status'] == '200':
		print 'returned status is OK'
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
	
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		
		return response
	else:
		print 'error logging out'
		# For whatever reason, the given token was invalid.
		
		response = make_response(json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		
		return response

@app.route('/create', methods=['POST'])
def newCategory(category):
	return None
	
@app.route('/JSON/<category>/')
def returnCategoryAsJson(category):
	dbCategory = getSpecificCategory(category)
	
	return json.dumps(dbCategory.__dict__)
	
@app.route('/JSON/<category>/<item>/')
def returnItemAsJson(category, item):
	dbItem = getItem(item)
	return json.dumps(dbItem.__dict__)
	
@app.route('/<category>/')
def showCategory(category):
	dbCategories = getCategories()
	dbCategory = getSpecificCategory(category)
	login_session['state'] = getRandomTokenString()
	""" return category """
	return render_template('category.html', category = dbCategory, categories = dbCategories, loggedIn = isUserLoggedIn(), STATE = login_session['state'])
		
@app.route('/<category>/update', methods=['POST'])
def updateCategory(category):
	if isUserLoggedIn() is not None:
		return isUserLoggedIn()
	elif request.args.get('state') != login_session['state']:
		response = make_response(json.dumps("Invalid state!"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		return 'Update category'
	
@app.route('/<category>/delete', methods=['POST'])
def deleteCategory(category):
	if isUserLoggedIn() is not None:
		return isUserLoggedIn()
	elif request.args.get('state') != login_session['state']:
		response = make_response(json.dumps("Invalid state!"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		return 'Delete category'
		
@app.route('/<category>/createItem', methods=['POST'])
def createItem(category, item):
	if isUserLoggedIn() is not None:
		return isUserLoggedIn()
	elif request.args.get('state') != login_session['state']:
		response = make_response(json.dumps("Invalid state!"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		categories = getCategories()
		dbCategory = getSpecificCategory(category)
		dbItem = getItem(item)
		
		return 'create item'
	
@app.route('/<category>/<item>/')
def showVariables(category, item):
	categories = getCategories()
	dbCategory = getSpecificCategory(category)
	dbItem = getItem(item)
	login_session['state'] = getRandomTokenString()
	
	return render_template('item.html', categories = categories, category = dbCategory, item = dbItem, loggedIn = isUserLoggedIn(), STATE = login_session['state'])
	
@app.route('/<category>/<item>/update', methods=['POST'])
def updateItem(category, item):
	if isUserLoggedIn() is not None:
		return isUserLoggedIn()
	elif request.args.get('state') != login_session['state']:
		response = make_response(json.dumps("Invalid state!"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		categories = getCategories()
		dbCategory = getSpecificCategory(category)
		dbItem = getItem(item)
		
		return 'update item'

@app.route('/<category>/<item>/delete', methods=['POST'])	
def deleteItem(category, item):
	if isUserLoggedIn() is not None:
		return isUserLoggedIn()
	elif request.args.get('state') != login_session['state']:
		response = make_response(json.dumps("Invalid state!"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		categories = getCategories()
		dbCategory = getSpecificCategory(category)
		dbItem = getItem(item)
		return 'delete item'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)