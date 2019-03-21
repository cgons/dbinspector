import logging
from datetime import date

import requests
from sqlalchemy.dialects.postgresql import insert

from . import db
from core.models import Station

logger = logging.getLogger(__name__)

engine = db.create_engine(db.get_db_uri())
session = db.session_factory(engine)


# Populate DB with Stations
# ------------------------------------------------------------------------------------------


def populate_stations():
    stations = fetch_stations()

    conn = engine.connect()
    conn.execute(
        insert(Station).on_conflict_do_nothing(),
        [dict(code=s["Code"], name=s["Name"]) for s in stations],
    )


def fetch_stations() -> list:
    try:
        date_str = date.today().strftime("%m%d%Y")
        url = f"https://secure.gotransit.com/service/EligibilityService.svc/GetDepartStations?dateString={date_str}"  # noqa
        resp = requests.get(url)
        return resp.json()["GetDepartStationsResult"]["Stations"]
    except Exception:
        logger.exception("Unable to fetch Stations.")

    return []


# Check Refund Eligibility
# ------------------------------------------------------------------------------------------


def check_eligibility_for_all_routes():
    # Get a list of routes from DB

    # For each route, get the trip timings (ie. "tripNumber")

    # For each timing in each route, check eligibility

    # Record status of route in a list if eligible

    # Store eligible routes in DB
    pass


def check_eligibility(
    date_str: str, arrival_station_code: str, trip_number: str
) -> bool:
    """Check refund eligibility of given route/date."""
    try:
        url = (
            "https://secure.gotransit.com/service/EligibilityService.svc/CheckEligible"
        )
        asc = arrival_station_code
        post_data = {
            "dateString": date_str,
            "arrivalstationCode": asc.upper(),
            "tripNumber": trip_number,
            "lang": "en",
        }
        resp = requests.post(url, json=post_data)
        if resp.json()["CheckEligibleResult"]["ResultType"] == 1:
            return True
    except Exception:
        logger.exception(
            f"Unable to determine eligibility status: "
            f"Arrival Station - {asc} | Trip No. - {trip_number}"
        )

    return False
