"""
	Database seed for Project 3
	Categories, Items, User Registration
	One Category contains many Items
	Registered users can perform CRUD operations on both Categories and Items
	
	Category
		Id int
		Name string
		
	Item
		Id int
		CategoryId int fk
		Name string
		Description string
"""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import json

print "dbSeed.py has begun"

Base = declarative_base()	
	
print Base

class Category(Base):
	__tablename__ = 'category'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	items = relationship("Item")
	
class Item(Base):
	__tablename__ = 'item'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	description = Column(String)
	category_id = Column(Integer, ForeignKey('category.id'))
	category = relationship(Category, backref=backref('categories', uselist=True))

def seedTheDB():
	#Reset the database.
	engine = create_engine('sqlite:///catalog.db')
	session = sessionmaker()
	session.configure(bind=engine)
	
	print "Dropping tables"
	Base.metadata.drop_all(engine)
	
	print "Creating tables"
	Base.metadata.create_all(engine)
		
	print "Creating records"
	
	Books = Category(name='Books')
	Movies = Category(name='Movies')
	
	TheSunAlsoRises = Item(name='The Sun Also Rises', description='By Ernest Hemingway about a group of American and British expatriates who travel from Paris to Pamplona.', category = Books)
	LOTR = Item(name="The Lord of the Rings", description="By JRR Tolkein, it's the grandfather of fantasy!", category=Books)
	Yojimbo = Item(name='Yojimbo', description='This Kurosawa movie is amazing!', category=Movies)
		
	s = session()
	s.add(Books)
	s.add(TheSunAlsoRises)
	s.add(Movies)
	s.add(Yojimbo)
	s.commit()
	
	engine.dispose()
	print "Finished initializing database.  Continuing to web server."
	
def checkTheDB():
	#If the database is not already initialized, initialize it.
	engine = create_engine('sqlite:///catalog.db')
	if engine.has_table('category'):
		print "Database exists.  Continuing to web server."
		engine.dispose()
	else:
		print "Database does not yet exist.  Initializing database."
		engine.dispose()
		seedTheDB()
	
	