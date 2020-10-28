#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate 
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)

# TODO: connect to a local postgresql database (Implementation: Done; Testing: ? )

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#set up Migrate
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate (Implementation: Done; Testing: ? )

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate (Implementation: Done; Testing: ? )

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data. (Done, Tested)
  #       num_shows should be aggregated based on number of upcoming shows per venue. (Done, Tested)
  try:
    #Get unique citiies 
    distinct_locs = Venue.query.distinct('city', 'state')
    data = []

    for loc in distinct_locs:
      venues = loc.query.filter(Venue.city==loc.city, Venue.state==loc.state)
      venueList = []
      for venue in venues:
        showCount = venue.query.join('shows').filter(Show.start_time >= datetime.now()).count()
        venueList.append({'id':venue.id, 'name': venue.name, 'num_upcoming_shows': showCount})
      data.append({'city': loc.city, 'state': loc.state, 'venues': venueList})
  finally:
    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. (done, tested)
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  try:
    search_term =  request.form.get('search_term', '')
    venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%'))
    data = []
    response = {}
    for venue in venues:
      showCount = venue.query.join('shows').filter(Show.start_time >= datetime.now()).count()
      data.append({"id": venue.id, "name": venue.name, "num_upcoming_shows": showCount})
    response = {"count": venues.count(), "data": data }

  except:
    error = True
    print(sys.exc_info())
  finally:
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id (done, tested)

  venue = Venue.query.get(venue_id)

  past_shows = Show.query.filter(Show.venue_id==venue_id).filter(Show.start_time < datetime.now())
  past_show_list = []
  past_shows_count = Show.query.filter(Show.venue_id==venue_id).filter(Show.start_time < datetime.now()).count()

  for show in past_shows:
    artist = Artist.query.get(show.artist_id)
    past_show_list.append({'artist_id': show.artist_id, 'artist_name': artist.name, 'artist_image_link': artist.image_link, 'start_time': str(show.start_time)})

  upcoming_shows = Show.query.filter(Show.venue_id==venue_id).filter(Show.start_time >= datetime.now())
  upcoming_show_list = []
  upcoming_shows_count = Show.query.filter(Show.venue_id==venue_id).filter(Show.start_time >= datetime.now()).count()

  for show in upcoming_shows:
    artist = Artist.query.get(show.artist_id)
    upcoming_show_list.append({'artist_id': show.artist_id, 'artist_name': artist.name, 'artist_image_link': artist.image_link, 'start_time': str(show.start_time)})

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_show_list,
    "upcoming_shows": upcoming_show_list,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    error = False
    name = request.form['name']
    state = request.form['state']
    city = request.form['city']
    address = request.form['address']
    phone = request.form['phone']
    tmp_genres = request.form.getlist('genres')
    genres = ','.join(tmp_genres)
    #facebook_link = request.form['facebook_link']
    venue = Venue(name=name, state=state, city=city, address=address, phone=phone, genres=genres)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    app.logger.error(f'{name}, {state}, {city}, {address}, {phone}')
  finally:
    db.session.close()
    return render_template('pages/home.html')
  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get(venue_id)
  venue.delete()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database (Done, Tested)
  data = []
  artists = Artist.query.all()
  for artist in artists:
    data.append({"id":artist.id, "name":artist.name})
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. (Done, Tested)
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))
  data=[]
  for artist in artists:
    upcoming_shows_count = Show.query.filter(Show.artist_id==artist.id).filter(Show.start_time >= datetime.now()).count()
    data.append({"id":artist.id, "name":artist.name, "num_upcoming_show": upcoming_shows_count})

  response={
    "count": artists.count(),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.get(artist_id)
  past_shows = Show.query.filter(Show.artist_id==artist_id).filter(Show.start_time < datetime.now())
  past_show_list = []
  past_shows_count = Show.query.filter(Show.artist_id==artist_id).filter(Show.start_time < datetime.now()).count()

  for show in past_shows:
    venue = Venue.query.get(show.venue_id)
    past_show_list.append({'venue_id': show.venue_id, 'venue_name': venue.name, 'venue_image_link': venue.image_link, 'start_time': str(show.start_time)})

  upcoming_shows = Show.query.filter(Show.artist_id==artist_id).filter(Show.start_time >= datetime.now())
  upcoming_show_list = []
  upcoming_shows_count = Show.query.filter(Show.artist_id==artist_id).filter(Show.start_time >= datetime.now()).count()

  for show in upcoming_shows:
    venue = Venue.query.get(show.venue_id)
    past_show_list.append({'venue_id': show.venue_id, 'venue_name': venue.name, 'venue_image_link': venue.image_link, 'start_time': str(show.start_time)})

  data={
    "id": artist.id,
    "name": artist.name,
    "genres": [artist.genres],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_show_list,
    "upcoming_shows": upcoming_show_list,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist = Artist.query.get(artist_id)
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": [artist.genres],
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.get(venue_id)

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id> Done, untested

  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name','')
    venue.genres = request.form.get('genres','')
    venue.address = request.form.get('address','')
    venue.city = request.form.get('city','')
    venue.state = request.form.get('state','')
    venue.phone = request.form.get('phone','')
    venue.facebook_link = request.form.get('facebook_link','')
    venue.commit()
  except:
    app.logger.error("Error editing venue")
    venue.rollback()
  finally:
    db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))
  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  try:
    name = request.form.get('name','')
    address = request.form.get('address','')
    city = request.form.get('city','')
    state = request.form.get('state','')
    phone = request.form.get('phone','')
    genres = request.form.get('genres','')
    facebook_link = request.form.get('facebook_link','')
    artist = Artist(name=name, address=address, city=city, state=state, phone=phone, genres=genres)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollbak()
    app.logger.error("Error creating artist")
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  finally:
    db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  data = []
  for show in shows:
    venue_name = Venue.query.get(show.venue_id).name
    artist_name = Artist.query.get(show.artist_id).name
    artist_image_link = Artist.query.get(show.artist_id).image_link
    data.append({"venue_id":show.venue_id, "venue_name": venue_name, "artist_id": show.artist_id, "artist_name": artist_name, "artist_image_link": artist_image_link, "start_time": str(show.start_time)})
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    artist_id = request.form.get('artist_id','')
    venue_id = request.form.get('venue_id','')
    start_time = request.form.get('start_time','')
    app.logger.error(f'{artist_id}, {venue_id}, {start_time}')
    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    flash('Show was successfully listed!')
    db.session.commit()
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
#if __name__ == '__main__':
#    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
