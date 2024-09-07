from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, ValidationError

class CharacterForm(FlaskForm):
    characters = StringField('Character name', validators=[DataRequired()])
    search = SubmitField('Search')