from flask import Flask
from flask import jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'
	
@app.route('/<category>/')
def showCategory(category):
	return 'Category: ' + category
	
@app.route('/<category>/<item>/')
def showVariables(category, item):
	return 'Category: ' + category + ', Item: ' + item
	
@app.route('/<category>/<item>/<protocol>/')
def showProtocolReturn(category, item, protocol):
	toReturn = 'Category: ' + category + ', Item: ' + item + ', Protocol: ' + protocol
	
	if protocol == "JSON":
		toReturn = jsonify(Category=category, Item=item, Protocol=protocol)


		
	return toReturn
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
	
"""
	Provide CRUD operations for Categories and Items
	URL should be //localhost:8000/<category>/<item>/<protocol>/<CRUD>
"""