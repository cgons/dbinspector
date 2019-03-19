from typing import Dict, List

from sqlalchemy.orm.session import Session
from sqlalchemy.dialects.postgresql import insert

from core import models as m


def insert_trips_for_route(
    dbsession: Session,
    depart_station_code: str,
    arrival_station_code: str,
    trips: List[Dict]
):
    for trip in trips:
        # Strip leading/trailing whitespace from trip values
        for k in trip:
            trip[k] = trip[k].strip()

        # Add route id to trip dict. (for inserting trips into DB)
        trip["depart_station_code"] = depart_station_code
        trip["arrival_station_code"] = arrival_station_code

    conn = dbsession.connection()
    stmt = insert(m.Trip).values(trips)
    stmt = stmt.on_conflict_do_update(
        index_elements=["trip_number"], set_=dict(trip_time=stmt.excluded.trip_time)
    )
    conn.execute(stmt)


def fetch_trips_for_route(depart_station_code, arrival_station_code):
    """Fetches trips from the GO site for the route provided."""

