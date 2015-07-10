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

engine = create_engine('sqlite:///catalog.db')

print engine

session = sessionmaker()

print session

session.configure(bind=engine)

print "Dropping tables"
Base.metadata.drop_all(engine)

print "Creating tables"
Base.metadata.create_all(engine)
	
print "Creating records"

Books = Category(name='Books')
Movies = Category(name='Movies')

print Books.name
print Movies.name

TheSunAlsoRises = Item(name='The Sun Also Rises', description='By Ernest Hemingway about a group of American and British expatriates who travel from Paris to Pamplona.', category = Books)
LOTR = Item(name="The Lord of the Rings", description="By JRR Tolkein, it's the grandfather of fantasy!", category=Books)
Yojimbo = Item(name='Yojimbo', description='This Kurosawa movie is amazing!', category=Movies)

'''print TheSunAlsoRises.name'''

s = session()
s.add(Books)
s.add(TheSunAlsoRises)
s.commit()
print "Items in database:"
for i in s.query(Item).all():
	print i.name
	
print "Categories in database:"
for i in s.query(Category).all():
	print i.name
	for d in i.items:
		print d.name
		
print 'Selecting a single category'
print s.query(Category).filter(Category.name  == 'Books').all()

for i in s.query(Category).filter(Category.name  == 'Books').all():
	print i.name
	
s.delete(Books)

print "After delete"
print "Categories in database:"
for i in s.query(Category).all():
	print i.name