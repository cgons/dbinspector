import logging

from flask import Flask
from sqlalchemy.ext.declarative import declarative_base

from . import utils
from . import db

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.config["SECRET_KEY"] = utils.read_auth_token_file()

engine = db.create_engine(db.get_db_uri())
session = db.make_app_scoped_session(app, engine)

Base = declarative_base(bind=engine)

from . import routes  # noqa

db.create_all_tables(Base)
