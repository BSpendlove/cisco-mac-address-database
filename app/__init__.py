from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
from app.views import (
    api_devices,
    api_users
)

from app import models

db.create_all()

app.register_blueprint(api_devices.bp)
app.register_blueprint(api_users.bp)