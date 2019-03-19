import logging
from typing import Dict

from sqlalchemy.orm.session import Session
from sqlalchemy.dialects.postgresql import insert

from core import models as m
from core.services import trip_service


logger = logging.getLogger(__name__)


def create_route_and_associated_trips(dbsession: Session, route_info: Dict):
    """Creates a Route entry in the system along with associated Trips.

    Note: If a route already exists, a duplicate route will not be created but Trip
    entries will be updated however.
    """
    try:
        # Upsert Routes
        conn = dbsession.connection()
        stmt = insert(m.Route).values(dict(
            depart_station_code=route_info["depart_station_code"],
            arrival_station_code=route_info["arrival_station_code"],
        ))
        stmt = stmt.on_conflict_do_nothing()
        conn.execute(stmt)

        # Upsert Trips
        trip_service.insert_trips_for_route(
            dbsession,
            route_info["depart_station_code"],
            route_info["arrival_station_code"],
            route_info["trips"],
        )
        dbsession.commit()
    except Exception:
        dbsession.rollback()
        logger.exception("ERROR - Unable to create Route + Trips")
    finally:
        dbsession.close()
