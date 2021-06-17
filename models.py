from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = "shows"

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)

    venue = db.relationship("Venue")
    venue_id = db.Column(
                        db.Integer,
                        db.ForeignKey("venues.id", ondelete="CASCADE"),
                        nullable=False
                        )

    artist = db.relationship("Artist")
    artist_id = db.Column(
                        db.Integer,
                        db.ForeignKey("artists.id",  ondelete="CASCADE"),
                        nullable=False
                        )


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields,
    # as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String(120)))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship(
                            'Show',
                            backref=db.backref('venues'),
                            lazy='joined',
                            cascade='all, delete',
                            )
    artists = db.relationship(
                            "Artist",
                            secondary="shows",
                            backref=db.backref('venue'),
                            lazy='joined',
                            cascade='all, delete',
                            )

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields,
    # as a database migration using Flask-Migrate
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship(
                            'Show',
                            backref=db.backref('artists'),
                            lazy='joined',
                            cascade='all, delete',
                            )
    venues = db.relationship(
                            "Venue",
                            secondary="shows",
                            backref=db.backref('artist'),
                            lazy='joined',
                            cascade='all, delete',
                            )

# TODO Implement Show and Artist models, and
# complete all model relationships and properties, as a database migration.
