import pytest
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def engine():
    engine = sa.create_engine("postgresql://postgres@localhost/postgres")
    conn = engine.connect()
    conn.execute("COMMIT")
    conn.execute("DROP DATABASE IF EXISTS testdb")

    conn.execute("COMMIT")
    conn.execute("CREATE DATABASE testdb")
    yield engine


@pytest.fixture
def dbsession(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


@pytest.fixture
def connection(dbsession):
    return dbsession.connection()
