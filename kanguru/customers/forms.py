from flask_wtf import FlaskForm
from wtforms import StringField, TextField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired
from datetime import datetime


class LoginForm(FlaskForm):
    username = StringField('Nazwa',
                           validators=[DataRequired()])
    password = PasswordField('Haslo',
                             validators=[DataRequired()])
    remember = BooleanField('Pamietaj mnie')
    submit = SubmitField('Login')


class CustomerForm(FlaskForm):
    details = StringField('Detale', validators=[DataRequired()])
    submit = SubmitField('Dodaj')


class SearchForm(FlaskForm):
    details = TextField()
    submit = SubmitField('Szukaj')
