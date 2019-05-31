from datetime import datetime
from kanguru import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Employee.query.get(int(user_id))


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.String(30), nullable=False)
    interactions = db.relationship('Interaction', backref='cust_interactions', lazy=True)


class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    details = db.Column(db.Text, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    bill = db.Column(db.Integer, nullable=False)
    paid = db.Column(db.Integer, nullable=False)


class Employee(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
