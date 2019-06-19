from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, DateTimeField, IntegerField
from wtforms.validators import DataRequired, InputRequired, ValidationError
from datetime import datetime


class InteractionForm(FlaskForm):
    details = TextField('Detale', validators=[DataRequired()])
    bill = IntegerField('Rachunek', validators=[InputRequired()])
    paid = IntegerField('Zaplacono', validators=[InputRequired()])
    date = DateTimeField('Data i godzina yyyy-mm-dd hh:mm', default=datetime.today, validators=[DataRequired()], format="%Y-%m-%d %H:%M")
    submit = SubmitField('Dodaj')

    def validate_date(self, date):
        if date.data > datetime.now():
            raise ValidationError('Data musi byc z przeszlosci!')
