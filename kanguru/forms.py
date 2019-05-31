from flask_wtf import FlaskForm
from wtforms import StringField, TextField, PasswordField, SubmitField, BooleanField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, InputRequired, Length, EqualTo, ValidationError, Email


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


class InteractionForm(FlaskForm):
    details = TextField('Detale', validators=[DataRequired()])
    bill = IntegerField('Rachunek', validators=[InputRequired()])
    paid = IntegerField('Platnosc', validators=[InputRequired()])
    date = DateTimeField('Data i godzina yyyy-mm-dd hh:mm', validators=[DataRequired()], format="%Y-%m-%d %H:%M")
    submit = SubmitField('Dodaj')


class SearchForm(FlaskForm):
    details = TextField()
    submit = SubmitField('Szukaj')
