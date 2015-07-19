Jesse Prevéy
July 12, 2015
Udacity Full-Stack Web Developer Nanodegree, Project 3

INSTRUCTIONS:

1- To run this file, you'll need to make sure you have Python and each of the 
required libraries installed.  First, download an installer package from 
https://www.python.org/downloads/ for Python 2, and run it.

2- Next, run the following command to install all the third party libraries 
required:

	sudo pip install flask sqlalchemy oauth2client httplib2 flask.ext.restless

3- Once you have the required libraries installed, navigate to the project 
folder: it should be '/vagrant/catalog/' within this project directory.

4- Once you are in the correct directory, use the following command to start 
the web server:

	python application.py
	
	This command begins the web server listening on http://localhost:8000/.
	Note: This application does not reset the database between runs.  If you 
	want to reset the database, use the following command:
	
		python -c 'import dbSeed; dbSeed.seedTheDB()'

REQUIREMENTS:

Python: 2.7.10 or later
https://www.python.org/downloads/
	Click the 'Download Python 2.x.x' button on this page to get an installer
	package for the latest version of Python 2.  Run that installer once it is
	downloaded.
	
Flask: 0.10.1 or later
http://flask.pocoo.org/

SQLAlchemy: 0.8.4 or later
http://www.sqlalchemy.org/

oauth2client: 1.4.12 or greater
https://pypi.python.org/pypi/oauth2client
		
httplib2: 0.9.1 or greater
https://pypi.python.org/pypi/httplib2/0.9.1
	
flask.ext.restless 
https://flask-restless.readthedocs.org/en/latest/installation.html
	
	
OPTIONAL:

This application was created using a Vagrant virtual machine; to use it as-is 
without needing to worry about installing extra Python libraries, just get and
install VirtualBox and Vagrant.

VirtualBox can be downloaded here: https://www.virtualbox.org/wiki/Downloads
Vagrant can be found here: https://www.vagrantup.com/downloads.html

Once you have Vagrant and VirtualBox up and running, open a command prompt and 
navigate to vagrant/ inside this directory, and run the following commands:

vagrant up
vagrant ssh

After that, you should be logged into the virtual machine used by this project.
Continue following the instructions after step 2.


FEATURES:
	This web application will allow you to browse Categories and Items, and will let you log in via your Google account to edit, create, and delete Items and Categories.
	
	This web application also features JSON endpoints for retrieving items: 
		http://localhost:8000/api/category for a list of categories,
		http://localhost:8000/api/item for a list of items.
		
	You can view JSON for individual objects with the following URLs:
		http://localhost:8000/api/category/<id>  where <id> is the ID of the category you want to view.
		http://localhost:8000/api/item/<id> where <id> is the ID of the item you want to view.
		
	NOTE: The library used for creating the JSON endpoints does not resolve URLs with trailing slashes.  Make sure to omit trailing slashes from API endpoint URL requests if you type them in by hand!


Third-party code sources:
	Google for their OAuth implementation and endpoint and for the jQuery JS library.
	Bootstrap for their CSS styles.
	jQuery for several Javascript helper functions and AJAX calls.
	The Udacity course "Authentication & Authorization: OAuth" (ud330) for a Python implementation of OAuth using Google as a provider.
	Flask for a ready-made web application framework for Python.
	SQLAlchemy for a Python ORM implementation.
	Flask.ext.restless for an easy Json API implementation.