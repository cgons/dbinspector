import pytest
import sqlalchemy as sa

from core import db, utils
from core.application import app, Base
from core import models as m


# Database Fixture Machinery
# ------------------------------------------------------------------------------------------
@pytest.fixture(scope="session")
def auth_token():
    return utils.read_auth_token_file()


@pytest.fixture(scope="session")
def engine():
    return db.create_engine(db.get_db_uri(dbname="gratestdb"))


@pytest.fixture
def dbsession(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = db.session_factory(engine)
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(dbsession):
    yield app.test_client()


class DBInspector(object):
    """
    Use as a context manager inspect the queries executed + query count.

    Usage:
        with DBSInspector(conn) as inspector:
            conn.execute("SELECT 1")
            conn.execute("SELECT 1")

            # Get query count
            assert inspector.get_count() == 2

            # Print queries issued
            inspector.log_queries(print_output=True, pretty=True)
    """
    def __init__(self, conn):
        self.conn = conn
        self.count = 0
        self.queries = []
        sa.event.listen(conn, 'after_execute', self.callback)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        sa.event.listen(self.conn, 'after_execute', self.callback)

    def get_count(self):
        return self.count

    def log_queries(self, print_output=False, print_pretty=False):
        if print_output:
            if print_pretty:
                for i, q in enumerate(self.queries, 1):
                    print(f"\nQUERY #{i}\n------------------------------------")
                    print(str(q))
            else:
                for q in self.queries:
                    print(str(q))

    def callback(self, conn, query, *args):
        self.queries.append(query)
        self.count += 1
# ------------------------------------------------------------------------------------------


@pytest.fixture()
def stations():
    return [
        m.Station(code="A", name="Station A"),
        m.Station(code="B", name="Station B"),
    ]


@pytest.fixture()
def routes():
    return [
        m.Route(depart_station_code="A", arrival_station_code="B")
    ]


@pytest.fixture()
def trips():
    return [
        m.Trip(
            depart_station_code="A", arrival_station_code="B", trip_number="101",
            trip_time="05:35"
        )
    ]
