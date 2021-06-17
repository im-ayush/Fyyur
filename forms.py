from models import *
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import (
                    StringField,
                    SelectField,
                    SelectMultipleField,
                    DateTimeField,
                    BooleanField
                    )
from wtforms.validators import (
                    DataRequired,
                    AnyOf,
                    URL,
                    Length,
                    Regexp,
                    ValidationError
                    )

from enums import State, Genre
import re

def is_valid_phone(phone):
    regex = re.compile('^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
    return regex.match(phone)

def validate_genres(genres):
    def _validate(form, field):
        error = False

        for value in field.data:
            if value not in genres:
                error = True

        if error:
            raise ValidationError('Not a valid option')

    return _validate

def is_valid_start_time(time):
    # 2021-04-07 16:47:43
    # datetime(*list(map(int, re.split("[- :]",time))))

    if datetime.now() <= time:
        return True
    return False

class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False

        if not Venue.query.get(self.venue_id.data):
            self.venue_id.errors.append("Invalid Venue.")
            return False
        if not Artist.query.get(self.artist_id.data):
            self.artist_id.errors.append("Invalid Artist.")
            return False
        if not is_valid_start_time(self.start_time.data):
            self.start_time.errors.append("Invalid Time.")
            return False
        return True

class VenueForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(),],
        choices = State.items()
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction
        'genres', validators=[
                            DataRequired(),
                            validate_genres([item.value for item in Genre])
                            ],
        choices = Genre.items()
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website = StringField(
        'website', validators=[URL()]
    )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField(
        'seeking_description'
    )

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if not is_valid_phone(self.phone.data):
            self.phone.errors.append('Invalid phone.')
            return False
        if not set(self.genres.data).issubset(dict(Genre.items()).keys()):
            self.genres.errors.append('Invalid genres.')
            return False
        if self.state.data not in dict(State.items()).keys():
            self.state.errors.append('Invalid state.')
            return False
        return True

class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        'state', validators=[DataRequired(),],
        choices=State.items()
    )
    phone = StringField(
        # TODO implement validation logic for state
        'phone'
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        'genres', validators=[
                            DataRequired(),
                            validate_genres([item.value for item in Genre])
                            ],
        choices = Genre.items()
     )
    facebook_link = StringField(
        # TODO implement enum restriction
        'facebook_link', validators=[URL()]
     )

    website = StringField(
        'website', validators=[URL()]
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
    )

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        if not is_valid_phone(self.phone.data):
            self.phone.errors.append('Invalid phone.')
            return False
        if not set(self.genres.data).issubset(dict(Genre.items()).keys()):
            self.genres.errors.append('Invalid genres.')
            return False
        if self.state.data not in dict(State.items()).keys():
            self.state.errors.append('Invalid state.')
            return False
        return True
