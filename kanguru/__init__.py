from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from kanguru.config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'customers.login'
login_manager.login_message_category = 'info'

from kanguru.customers.routes import bp_customers
from kanguru.interactions.routes import bp_interactions

app.register_blueprint(bp_customers)
app.register_blueprint(bp_interactions)
