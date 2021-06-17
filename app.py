#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import (
            Flask,
            render_template,
            request,
            Response,
            flash,
            redirect,
            url_for,
            jsonify,
            abort
            )
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from models import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import or_
import sys

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
CSRFProtect(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

# MODELS

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
    # TODO: replace with real venues data.
            # num_shows should be aggregated based on
            # number of upcoming shows per venue.

    data_areas = []

    areas = Venue.query \
        .with_entities(Venue.city, Venue.state) \
        .group_by(Venue.city, Venue.state) \
        .all()

    for area in areas:
        areas = []
        venues = Venue.query.all()

        places = Venue.query.distinct(Venue.city, Venue.state).all()

        for place in places:
            areas.append({
                    'city': place.city,
                    'state': place.state,
                    'venues': [{
                        'id': venue.id,
                        'name': venue.name,
                        'num_upcoming_shows': len([
                                    show for show in venue.shows
                                    if show.start_time > datetime.now()
                            ])
                    } for venue in venues if
                        venue.city==place.city and venue.state==place.state
                    ]
            })
    return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search.
    #       Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and
    # "Park Square Live Music & Coffee"

    search_term = request.form['search_term']
    search = "%{}%".format(search_term.lower())

    venues = Venue.query \
        .with_entities(Venue.id, Venue.name) \
        .filter(Venue.name.ilike(search)) \
        .all()

    data_venues = []

    for venue in venues:
        upcoming_shows = db.session \
                .query(Show) \
                .filter(Show.venue_id == venue.id) \
                .filter(Show.start_time > datetime.now()) \
                .all()

        data_venues.append({
            'id': venue.id,
            'name': venue.name,
            'num_upcoming_shows': len(upcoming_shows)
        })

    results = {'venues': data_venues, 'count': len(venues)}
    return render_template(
                        'pages/search_venues.html',
                        results=results,
                        search_term=search_term
                        )

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.filter_by(id=venue_id).first_or_404()

    past_shows_query = db.session.query(Show).join(Artist) \
                        .filter(Show.venue_id==venue_id) \
                        .filter(Show.start_time<datetime.now()) \
                        .all()

    past_shows = []

    for show in past_shows_query:
        if show.start_time <= datetime.now():
            past_shows.append({
                'artist_id': show.artist_id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.strftime('%b-%d-%Y, %I:%M %p')
            })

    upcoming_shows_query = db.session.query(Show).join(Artist) \
                            .filter(Show.venue_id==venue_id) \
                            .filter(Show.start_time>datetime.now()) \
                            .all()

    upcoming_shows = []
    for show in upcoming_shows_query:
        if show.start_time > datetime.now():
            upcoming_shows.append({
                'artist_id': show.artist_id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'start_time': show.start_time.strftime('%b-%d-%Y, %I:%M %p')
            })

    data = {
        'id': venue.id,
        'name': venue.name,
        'city': venue.city,
        'address': venue.address,
        'state': venue.state,
        'phone': venue.phone,
        'image_link': venue.image_link,
        'facebook_link': venue.facebook_link,
        'website': venue.website,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'genres': venue.genres,

        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows),
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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    error = False
    form = VenueForm(request.form, meta={'csrf':False})

    if form.validate():
        try:
            venue = Venue()
            form.populate_obj(venue)
            db.session.add(venue)
            db.session.commit()

        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors'+ str(message))
    return render_template('pages/home.html')

    # on successful db insert, flash success
    # flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name +
    #             ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record.
    # Handle cases where the session commit could fail.
    error = False

    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
        print(sys.exc_info())
        return render_template('errors/500.html', error=str(e))
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page,
    #                   have it so that clicking that button delete it
    #                   from the db then redirect the user to the homepage
    if error:
        abort(400)
        return jsonify({ 'success': False })
    else:
        return jsonify({ 'success': True })


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data_artists = []

    artists = Artist.query \
        .with_entities(Artist.id, Artist.name) \
        .order_by('id') \
        .all()

    for artist in artists:
        upcoming_shows = db.session \
                .query(Show) \
                .filter(Show.artist_id == artist.id) \
                .filter(Show.start_time > datetime.now()) \
                .all()

        data_artists.append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': len(upcoming_shows)
        })
    return render_template('pages/artists.html', artists=data_artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search.
    #       Ensure it is case-insensitive.
    # search for "A" should return "Guns N Petals", "Matt Quevado",
    #       and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form['search_term']
    search = "%{}%".format(search_term.lower())

    artists = Artist.query \
        .with_entities(Artist.id, Artist.name) \
        .filter(Artist.name.ilike(search)) \
        .all()

    data_artists = []
    for artist in artists:
        upcoming_shows = db.session \
                .query(Show) \
                .filter(Show.artist_id == artist.id) \
                .filter(Show.start_time > datetime.now()) \
                .all()

        data_artists.append({
            'id': artist.id,
            'name': artist.name,
            'num_upcoming_shows': len(upcoming_shows)
        })

    results = {'data': data_artists, 'count': len(artists)}

    return render_template(
                        'pages/search_artists.html',
                        results=results,
                        search_term=search_term
                        )

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table,
    #       using artist_id

    artist = Artist.query.filter_by(id=artist_id).first_or_404()

    past_shows_query = db.session.query(Show).join(Venue) \
                        .filter(Show.artist_id==artist_id) \
                        .filter(Show.start_time<datetime.now()) \
                        .all()

    past_shows = []
    for show in past_shows_query:
        if show.start_time <= datetime.now():
            past_shows.append({
                'venue_id': show.venue_id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'start_time': show.start_time.strftime('%b-%d-%Y, %I:%M %p')
            })

    upcoming_shows_query = db.session.query(Show).join(Venue) \
                            .filter(Show.artist_id==artist_id) \
                            .filter(Show.start_time>datetime.now()) \
                            .all()
    upcoming_shows = []

    for show in upcoming_shows_query:
        if show.start_time > datetime.now():
            upcoming_shows.append({
                'venue_id': show.venue_id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'start_time': show.start_time.strftime('%b-%d-%Y, %I:%M %p')
            })

    data = {
        'id': artist.id,
        'name': artist.name,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'image_link': artist.image_link,
        'facebook_link': artist.facebook_link,
        'website': artist.website,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'genres': artist.genres,

        'past_shows': past_shows,
        'upcoming_shows': upcoming_shows,
        'past_shows_count': len(past_shows),
        'upcoming_shows_count': len(upcoming_shows),
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    artist = Artist.query.filter_by(id=artist_id).first_or_404()
    form = ArtistForm(obj=artist)

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error = False
    form = ArtistForm(request.form, meta={'csrf':False})

    if form.validate():
        try:
            artist = Artist.query.get(artist_id)
            form.populate_obj(artist)
            db.session.commit()
            flash('Artist ('+str(artist_id)+') was successfully updated!','success')


        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors'+ str(message))

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # venue = Venue.query.filter(Venue.id == venue_id).first()
    venue = Venue.query.filter_by(id=venue_id).first_or_404()
    form = VenueForm(obj=venue)

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    error = False
    form = VenueForm(request.form, meta={'csrf':False})

    if form.validate():
        try:
            venue = Venue.query.get(venue_id)
            form.populate_obj(venue)
            db.session.commit()
            flash('Venue ('+str(venue_id)+') was successfully updated!','success')

        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors'+ str(message))

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
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    error = False
    form = ArtistForm(request.form, meta={'csrf':False})

    if form.validate():
        try:
            artist = Artist()
            form.populate_obj(artist)
            db.session.add(artist)
            db.session.commit()

        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()
    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
        flash('Errors'+ str(message))

    # on successful db insert, flash success
    # flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name +
    #               ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of
    #       upcoming shows per venue.

    data = []

    shows = db.session \
        .query(
          Venue.name,
          Artist.name,
          Artist.image_link,
          Show.venue_id,
          Show.artist_id,
          Show.start_time
        ) \
        .filter(Venue.id == Show.venue_id, Artist.id == Show.artist_id)

    for show in shows:
        data.append({
          'venue_name': show[0],
          'artist_name': show[1],
          'artist_image_link': show[2],
          'venue_id': show[3],
          'artist_id': show[4],
          'start_time': show[5].strftime('%b-%d-%Y, %I:%M %p')
        })
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db,
    # upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    error = False
    form = ShowForm(request.form, meta={'csrf':False})

    if form.validate():
        try:
            show  = Show()
            form.populate_obj(show)
            db.session.add(show)
            db.session.commit()
            flash('Show added successfully.')

        except Exception:
            error = True
            db.session.rollback()
            print(sys.exc_info())

        finally:
            db.session.close()

    else:
        message = []
        for field, err in form.errors.items():
            message.append(field + ' ' + '|'.join(err))
            flash('Errors'+ str(message))
    # on successful db insert, flash success
    # flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/shows/search', methods=['POST'])
def search_shows():
    search_term = request.form['search_term']
    search = "%{}%".format(search_term.lower())

    shows = db.session \
        .query(
          Venue.name,
          Artist.name,
          Artist.image_link,
          Show.venue_id,
          Show.artist_id,
          Show.start_time
        ) \
        .filter(or_(Venue.name.ilike(search), Artist.name.ilike(search)))

    data=[]
    for show in shows:
        data.append({
          'venue_name': show[0],
          'artist_name': show[1],
          'artist_image_link': show[2],
          'venue_id': show[3],
          'artist_id': show[4],
          'start_time': str(show[5].strftime('%b-%d-%Y, %I:%M %p'))
        })


    results = {'data': data, 'count': len(data)}

    return render_template(
                        'pages/show.html',
                        results=results,
                        search_term=search_term
                        )



@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
                            Formatter(
                            '%(asctime)s %(levelname)s: \
                            %(message)s [in %(pathname)s:%(lineno)d]'
                            ))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
