from flask import render_template, Blueprint
from kanguru import db
from flask_login import login_required
from sqlalchemy.sql import func
from kanguru.models import Interaction
from datetime import datetime, timedelta

bp_statistics = Blueprint('all_statistics', __name__)


@bp_statistics.route("/all_statistics")
@login_required
def all_statistics():

    lm_year = (datetime.now() - timedelta(days=datetime.now().day + 1)).year
    lm_month = (datetime.now() - timedelta(days=datetime.now().day + 1)).month

    lm_bill = db.session.query(func.coalesce(func.sum(Interaction.bill), 0)).filter(func.extract('year', Interaction.date) == lm_year).filter(func.extract('month', Interaction.date) == lm_month).first()
    lm_paid = db.session.query(func.coalesce(func.sum(Interaction.paid), 0)).filter(func.extract('year', Interaction.date) == lm_year).filter(func.extract('month', Interaction.date) == lm_month).first()

    try:
        lm_debt = lm_paid[0] - lm_bill[0]
    except:
        lm_debt = 0

    h_bill = db.session.query(func.coalesce(func.sum(Interaction.bill), 0)).first()
    h_paid = db.session.query(func.coalesce(func.sum(Interaction.paid), 0)).first()

    try:
        h_debt = h_paid[0] - h_bill[0]
    except:
        h_debt = 0

    return render_template('all_statistics.html', title='Statystyki', lm_month=lm_month, lm_year=lm_year, lm_debt=lm_debt, lm_bill=lm_bill[0], h_debt=h_debt, h_bill=h_bill[0])
