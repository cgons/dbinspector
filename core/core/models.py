import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .application import Base


class User(Base):
    __tablename__ = "user"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.String(255), unique=True, nullable=False)


class Station(Base):
    __tablename__ = "station"

    code = sa.Column(sa.String(255), primary_key=True)
    name = sa.Column(sa.String(255), unique=True)

    @staticmethod
    def get_stations(session, filter_exp=None):
        query = session.query(Station)
        if filter_exp is not None:
            query = query.filter(filter_exp)
        return query.all()


class Route(Base):
    __tablename__ = "route"

    # Columns
    # ---
    id = sa.Column(sa.Integer, primary_key=True)
    depart_station_code = sa.Column(sa.String(255), sa.ForeignKey("station.code"))
    arrival_station_code = sa.Column(sa.String(255), sa.ForeignKey("station.code"))

    # Relationships
    # ---
    depart_station = relationship(
        "Station", foreign_keys=[depart_station_code], lazy="joined"
    )
    arrival_station = relationship(
        "Station", foreign_keys=[arrival_station_code], lazy="joined"
    )
    trips = relationship("Trip", backref="route", lazy="subquery")

    # Constraints
    # ---
    __table_args__ = (
        sa.UniqueConstraint("depart_station_code", "arrival_station_code"),
    )

    # Methods
    # ---
    def serialize(self):
        """Return a fully JSON serializable dict of a route, associated depart and arrival
        station names + associated trips."""
        return {
            "depart_station": self.depart_station.name,
            "depart_station_code": self.depart_station_code,
            "arrival_station": self.arrival_station.name,
            "arrival_station_code": self.arrival_station_code,
            "trips": [
                dict(trip_number=t.trip_number, trip_time=t.trip_time)
                for t in self.trips
            ],
        }


class Trip(Base):
    __tablename__ = "trip"

    trip_number = sa.Column(sa.String(255), primary_key=True)
    trip_time = sa.Column(sa.String(255), nullable=False)
    route_id = sa.Column(sa.Integer, sa.ForeignKey("route.id"))
