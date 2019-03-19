import os

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy_session import flask_scoped_session


def get_db_uri(
        host="localhost", username="postgres", password="postgres", dbname="gra", port=5432
):
    host = os.environ.get("DB_HOST", host)
    username = os.environ.get("DB_USERNAME", username)
    password = os.environ.get("DB_PASSWORD", password)
    dbname = os.environ.get("DB_NAME", dbname)
    return f"postgresql://{username}:{password}@{host}:{port}/{dbname}"


def session_factory(engine, **kwargs):
    Session = sessionmaker(bind=engine, **kwargs)
    return Session()


def make_app_scoped_session(app, engine, **kwargs):
    Session = sessionmaker(bind=engine, **kwargs)
    return flask_scoped_session(Session, app)


def create_engine(db_uri: str):
    return sa.create_engine(db_uri)


def create_all_tables(base):
    base.metadata.create_all()

    # # Mark migrations as up-to-date
    # from alembic.config import Config
    # from alembic import command
    # alembic_ini_path = os.path.join(os.getcwd(), "..", "alembic.ini")
    # alembic_cfg = Config(alembic_ini_path)
    # command.stamp(alembic_cfg, "head")
