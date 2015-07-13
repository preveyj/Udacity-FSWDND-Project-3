Jesse Prevéy
July 12, 2015
Udacity Full-Stack Web Developer Nanodegree, Project 3

INSTRUCTIONS:

To run this file, you'll need Vagrant and VirtualBox installed.

VirtualBox can be downloaded here: https://www.virtualbox.org/wiki/Downloads
Vagrant can be found here: https://www.vagrantup.com/downloads.html

Once you have Vagrant and VirtualBox up and running, open a command prompt and 
navigate to vagrant/ inside this directory, and run the following commands:

vagrant up
vagrant ssh

That will install and configure the Vagrant VM needed for this project, and log 
into an SSH session on the VM.  Once you're logged in, run the following
command to seed the database:

python -c 'import dbSeed; dbSeed.seedTheDB()'

That command will create a Sqlite database file called 'catalog.db' if it 
doesn't already exist, wipe it out, recreate the relevant tables, and seed the
tables with sample data.

Once that command has completed, start the web server with this command:

python application.py

That will start a webserver running on //localhost:8000/; visit that page to 
get started with the catalog app.


Third-party code sources:
	Google for their OAuth implementation and endpoint and for the jQuery JS library.
	Bootstrap for their CSS styles.
	jQuery for several Javascript helper functions and AJAX calls.
	The Udacity course "Authentication & Authorization: OAuth" (ud330) for a Python implementation of OAuth using Google as a provider.
	Flask for a ready-made web application framework for Python.
	SQLAlchemy for a Python ORM implementation.