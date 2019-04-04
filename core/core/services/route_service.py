import logging
from typing import Dict

from sqlalchemy.orm.session import Session
from sqlalchemy.dialects.postgresql import insert

from core import exceptions, models as m
from core.services import trip_service


logger = logging.getLogger(__name__)


def create_route_and_associated_trips(
    dbsession: Session, route_info: Dict, user_id: int
):
    """Creates a Route entry in the system along with associated Trips.

    Note: If a route already exists, a duplicate route will not be created but Trip
    entries will be updated however.
    """
    try:
        codes = dict(
            depart_station_code=route_info["depart_station_code"],
            arrival_station_code=route_info["arrival_station_code"],
        )

        # Upsert Routes
        conn = dbsession.connection()
        stmt = insert(m.Route).values(codes)
        stmt = stmt.on_conflict_do_nothing()
        conn.execute(stmt)

        route_id = dbsession.query(m.Route.id).filter_by(**codes).scalar()

        # Associate route with user
        dbsession.add(m.UserRoute(user_id=user_id, route_id=route_id))

        # Fetch and upsert trips (from GO API) for route
        trips = trip_service.fetch_trips_for_route(**codes)
        trip_service.insert_trips_for_route(dbsession, route_id, trips)

        dbsession.commit()
    except:
        dbsession.rollback()
        logger.exception("ERROR - Unable to create Route + Trips")
        raise  # will re-raise the last exception
    finally:
        dbsession.close()


def delete_user_route_association(dbsession: Session, user_id: int, route_id: int):
    dbsession.query(m.UserRoute).filter_by(user_id=user_id, route_id=route_id).delete()
    dbsession.commit()
