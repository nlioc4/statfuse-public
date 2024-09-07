from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired, ValidationError, EqualTo

class CharacterForm2(FlaskForm):
    characters2 = StringField('Character name')
    run_report = SubmitField('Run Report')

class TestAltCharacterForm(FlaskForm):
    characters = StringField('Character name', validators=[DataRequired()])
    altText = StringField('Alt Search')
    alts = SelectMultipleField('Alts', choices=[])
    search = SubmitField('Search')