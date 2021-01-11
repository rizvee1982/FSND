import os
from sqlalchemy import Column, String, Integer, DateTime, create_engine
from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
import json

database_name = "castingagency"
database_path = "postgres://{}/{}".format('localhost:5432', database_name)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_path

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

movie_actors  = db.Table('movieactors',
                    Column('movie_id', Integer, db.ForeignKey('movies.id')),
                    Column('actor_id', Integer, db.ForeignKey('actors.id')))

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
  app.config["SQLALCHEMY_DATABASE_URI"] = database_path
  app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
  db.app = app
  db.init_app(app)
  db.create_all()

'''
Movie

'''
class Movie(db.Model):  
  __tablename__ = 'movies'

  id = Column(Integer, primary_key=True)
  title = Column(String)
  release_date = Column(String)
  actors = db.relationship("Actor",
              secondary=movie_actors,
              back_populates="movies")

  def __init__(self, title, release_date):
    self.title = title
    self.release_date = release_date

  def insert(self):
    db.session.add(self)
    db.session.commit()

  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'title': self.title,
      'release_date': self.release_date,
    }

'''
Actor

'''

class Actor(db.Model):  
  __tablename__ = 'actors'

  id = Column(Integer, primary_key=True)

  movies = db.relationship("Movie",
            secondary=movie_actors,
            back_populates="actors")

  age = Column(Integer)
  gender = Column(String)
  name = Column(String)

  def __init__(self, name, gender, age):
    self.age = age
    self.gender = gender
    self.name = name
  
  def insert(self):
    db.session.add(self)
    db.session.commit()

  def update(self):
    db.session.commit()

  def delete(self):
    db.session.delete(self)
    db.session.commit()

  def format(self):
    return {
      'id': self.id,
      'name': self.name,
      'gender': self.gender,
      'age': self.age
    }



if __name__ == '__main__':
    manager.run()

