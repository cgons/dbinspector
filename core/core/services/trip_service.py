import datetime
import logging
from typing import Dict, List

import requests
from sqlalchemy.orm.session import Session
from sqlalchemy.dialects.postgresql import insert

from core import models as m
from core import exceptions


logger = logging.getLogger(__name__)


GO_API_TRIPS_URL = (
    "https://secure.gotransit.com/service/EligibilityService.svc/"
    "GetTrips?dateString={date_string}&fromStation={depart_station_code}"
    "&tostation={arrival_station_code}"
)


def insert_trips_for_route(dbsession: Session, route_id: int, trips: List[Dict]):
    trips = [
        dict(
            route_id=route_id,
            trip_number=str(trip["TripNumber"]).strip(),
            trip_time=trip["DepartTime"].strip(),
        )
        for trip in trips
    ]

    conn = dbsession.connection()
    stmt = insert(m.Trip).values(trips)
    stmt = stmt.on_conflict_do_update(
        index_elements=["trip_number"], set_=dict(trip_time=stmt.excluded.trip_time)
    )
    conn.execute(stmt)


def fetch_trips_for_route(depart_station_code, arrival_station_code):
    """Fetches trips from the GO site for the route provided."""
    date_string = datetime.date.today().strftime("%m%d%Y")
    uri = GO_API_TRIPS_URL.format(
        date_string=date_string,
        depart_station_code=depart_station_code,
        arrival_station_code=arrival_station_code,
    )
    try:
        resp = requests.get(uri)
        return resp.json()["GetTripsResult"]["Trips"]
    except Exception:
        logger.exception(
            "Unable to fetch Trips from GO API for route: "
            "{depart_station_code} - {arrival_station_code}"
        )
        raise exceptions.UnableToFetchTripsException()
