import requests
import random
import string
import json
import sys
import traceback
from flask import Flask, jsonify, render_template, make_response
from flask import flash, redirect, url_for, request
from flask import session as login_session
from flask import __version__ as FlaskVersion
from sqlalchemy import create_engine
from sqlalchemy import __version__ as AlchemyVersion
from sqlalchemy.orm import sessionmaker
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import flask.ext.restless
import dbSeed
from dbSeed import Category, Item

app = Flask(__name__)
app.debug = True

# This key should normally be hard to guess, like a strong password. For now,
# we're going to use something simple.
 
app.secret_key = 'super secret key'

engine = create_engine('sqlite:///catalog.db')
session = sessionmaker()
session.configure(bind=engine)
s = session()
manager = flask.ext.restless.APIManager(app, session = s)

category_blueprint = manager.create_api(Category, methods=['GET'])
item_blueprint = manager.create_api(Item, methods=['GET'])

CLIENT_ID = json.loads(
		open('client_secrets.json', 'r').read()
	)['web']['client_id']

# Check and initialize the database if needed.
dbSeed.checkTheDB()

# Helper methods to improve code reuse
def getCategories():
	return s.query(Category).all()

def getSpecificCategory(categoryId):
	return s.query(Category).filter(Category.id == categoryId).first()
	
def getItem(itemId):
	return s.query(Item).filter(Item.id == itemId).first()

# This is one of the methods borrowed from ud330
def getRandomTokenString():
	return ''.join(
		random.choice(
				string.ascii_uppercase + string.digits
			) for x in xrange(32)
		)

def isUserLoggedIn():
	# Check if the user is logged in.  'username' should be in login_session
	# if the user is logged in.
	if 'username' not in login_session:
		return False
	else:
		return True

# Route definitions
@app.route('/')
def hello_world():
	categories = getCategories()
	login_session['state'] = getRandomTokenString()
			
	return render_template(
			'index.html', 
			categories = categories, 
			loggedIn = isUserLoggedIn(), 
			STATE = login_session['state']
		)
	
@app.route('/getVersions')
def getVersions():
	return 'Flask: ' + FlaskVersion + ', SQLAlchemy: ' + AlchemyVersion
	
# This is another method borrowed from ud330, and remains mostly unchanged.
@app.route('/gconnect', methods=['POST'])
def gconnect():
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
		response = make_response(
				json.dumps('Failed to upgrade the authorization code.'), 
				401
			)
			
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
		response = make_response(
				json.dumps("Token's user ID doesn't match given user ID."),
				401
			)
			
		response.headers['Content-Type'] = 'application/json'
		return response
		
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
				json.dumps("Token's client ID does not match app's"), 
				401
			)
			
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')

	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(
				json.dumps('Current user is already connected.'), 
				200
			)
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
		response = make_response(
				json.dumps('Current user not connected.'), 401
			)
			
		response.headers['Content-Type'] = 'application/json'
		return response
		
	access_token = credentials
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	
	if result['status'] == '200':
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
	
		response = make_response(json.dumps('Successfully disconnected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		
		return response
	else:
		# For whatever reason, the given token was invalid.
		
		response = make_response(
				json.dumps('Failed to revoke token for given user. Doing hard logout.', 400)
			)
			
		del login_session['credentials']
		del login_session['gplus_id']
		del login_session['username']
		del login_session['email']
			
		response.headers['Content-Type'] = 'application/json'
		
		return response

@app.route('/catalog/create', methods=['POST'])
def newCategory():	
	if isUserLoggedIn() == False:
		return render_template('loginError.html')
	elif request.form['state'] != login_session['state']:
		response = make_response(json.dumps("Invalid state!"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		# DB operations
		try:
			NewCategory = Category(name = request.form['name'])
			s.add(NewCategory)
			s.commit()
		
			response = make_response(json.dumps(NewCategory.id), 200)
			response.headers['Content-Type'] = 'application/json'
			return response
			
		except:
			response = make_response(json.dumps("Error!"), 500)
			response.headers['Content-Type'] = 'application/json'
			return response
	
@app.route('/catalog/<category>/')
def showCategory(category):
	dbCategories = getCategories()
	dbCategory = getSpecificCategory(category)
	login_session['state'] = getRandomTokenString()
	return render_template(
			'category.html', 
			category = dbCategory, 
			categories = dbCategories, 
			loggedIn = isUserLoggedIn(), 
			STATE = login_session['state']
		)
		
@app.route('/catalog/<category>/update', methods=['POST'])
def updateCategory(category):
	
	if isUserLoggedIn() == False:
		return render_template('loginError.html')
	elif request.form['state'] != login_session['state']:
		response = make_response(json.dumps("Invalid state!"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		try:
			CategoryToUpdate = getSpecificCategory(category)
			CategoryToUpdate.name = request.form['name']
			s.add(CategoryToUpdate)
			s.commit()
		except:
			response = make_response(json.dumps("Error!"), 500)
			response.headers['Content-Type'] = 'application/json'
			return response
		
		response = make_response(json.dumps("Category updated!"), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
	
@app.route('/catalog/<category>/delete', methods=['POST'])
def deleteCategory(category):
	
	if isUserLoggedIn() == False:
		return render_template('loginError.html')
	elif request.form['state'] != login_session['state']:
		response = make_response(json.dumps("Invalid state!"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		try:
			CategoryToDelete = getSpecificCategory(category)
			s.delete(CategoryToDelete)
			s.commit()
		except:
			response = make_response(json.dumps("Error!"), 500)
			response.headers['Content-Type'] = 'application/json'
			return response
			
		response = make_response(json.dumps("Category deleted!"), 200)
		response.headers['Content-Type'] = 'application/json'
		return response
		
# User submits a new item
@app.route('/catalog/<category>/submitItem', methods=['POST'])
def submitItem(category):
	if isUserLoggedIn() == False:
		return render_template('loginError.html')
	elif request.form['state'] != login_session['state']:
		response = make_response(json.dumps("Invalid state!"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		try:
			ItemToUpdate = getItem(request.form['id'])
			if (ItemToUpdate is not None):
				ItemToUpdate.name = request.form['name']
				ItemToUpdate.description = request.form['description']
			else:
				ParentCategory = getSpecificCategory(request.form['category'])
				ItemToUpdate = Item(
						name = request.form['name'], 
						description = request.form['description'], 
						category = ParentCategory
					)
			
			s.add(ItemToUpdate)
			s.commit()
		except:
			response = make_response(json.dumps("Error!"), 500)
			response.headers['Content-Type'] = 'application/json'
			return response
			
		response = make_response(json.dumps(ItemToUpdate.id), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

# User wants to create a new item; show the editItem.html template
@app.route('/catalog/<category>/createItem')
def createItem(category):
	if isUserLoggedIn() == False:
		return render_template('loginError.html')
	elif request.args.get('state') != login_session['state']:
		response = make_response(json.dumps("Invalid state!"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		categories = getCategories()
		dbCategory = getSpecificCategory(category)
		login_session['state'] = getRandomTokenString();
		# The Jinja filter tests "if item is defined", but None counts as 
		# 'defined', so we omit the item this time.
		return render_template(
				'editItem.html', 
				categories = categories, 
				category = dbCategory, 
				loggedIn = isUserLoggedIn(), 
				STATE = login_session['state']
			)
	
@app.route('/catalog/<category>/<item>/')
def showVariables(category, item):
	categories = getCategories()
	dbCategory = getSpecificCategory(category)
	dbItem = getItem(item)
	login_session['state'] = getRandomTokenString()
	
	return render_template(
			'item.html', 
			categories = categories, 
			category = dbCategory, 
			item = dbItem, 
			loggedIn = isUserLoggedIn(), 
			STATE = login_session['state']
		)
	
@app.route('/catalog/<category>/<item>/edit')
def showItemEditTemplate(category, item):	
	if isUserLoggedIn() == False:
		return render_template('loginError.html')
	elif request.args.get('state') != login_session['state']:
		response = make_response(json.dumps("Invalid state!"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		categories = getCategories()
		dbCategory = getSpecificCategory(category)
		dbItem = getItem(item)
		login_session['state'] = getRandomTokenString();
		
		return render_template(
				'editItem.html', 
				item = dbItem, 
				categories = categories, 
				category = dbCategory, 
				loggedIn = isUserLoggedIn(), 
				STATE = login_session['state']
			)

@app.route('/catalog/<category>/<item>/delete', methods=['POST'])	
def deleteItem(category, item):
	if isUserLoggedIn() == False:
		return render_template('loginError.html')
	elif request.form['state'] != login_session['state']:
		response = make_response(json.dumps("Invalid state!"), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	else:
		try:
			ItemToDelete = getItem(request.form['id'])
			s.delete(ItemToDelete)
			s.commit()
		except:
			response = make_response(json.dumps("Error!"), 500)
			response.headers['Content-Type'] = 'application/json'
			return response
			
		response = make_response(json.dumps("Item deleted!"), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)