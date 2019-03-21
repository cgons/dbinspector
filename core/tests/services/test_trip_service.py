import datetime

import pytest
import simplejson as json
import requests_mock

from core import models as m
from core import exceptions
from core.services import trip_service


def test_insert_trips_for_route(dbsession, stations, routes):
    """Ensure trips are inserted correctly (w/ leading/trailing whitespace removed)."""
    dbsession.add_all(stations + routes)
    dbsession.commit()

    assert dbsession.query(m.Trip).count() == 0

    trips = [dict(TripNumber="   102", DepartTime="05:45   ")]
    trip_service.insert_trips_for_route(dbsession, 1, trips)

    trips = dbsession.query(m.Trip).all()
    assert len(trips) == 1

    trip = trips[0]
    assert trip.trip_number == "102"
    assert trip.trip_time == "05:45"
    assert trip.route_id == 1


def test_insert_trips_for_route_updates_trip(dbsession, stations, routes, trips):
    """Ensure duplicate trips provided update existing rows vs. create new rows."""
    dbsession.add_all(stations + routes + trips)
    dbsession.commit()

    assert dbsession.query(m.Trip).count() == 1

    trips = [dict(TripNumber="101", DepartTime="05:55")]
    trip_service.insert_trips_for_route(dbsession, 1, trips)

    trips = dbsession.query(m.Trip).all()
    assert len(trips) == 1

    trip = trips[0]
    assert trip.trip_number == "101"
    assert trip.trip_time == "05:55"
    assert trip.route_id == 1


def test_fetch_trips_for_route(trips_api_resp):
    date_string = datetime.date.today().strftime("%m%d%Y")
    uri = trip_service.GO_API_TRIPS_URL.format(
        date_string=date_string, depart_station_code="A", arrival_station_code="B"
    )

    with requests_mock.Mocker() as m:
        m.get(uri, json=json.loads(trips_api_resp))
        trips = trip_service.fetch_trips_for_route("A", "B")

        assert len(trips) > 0

        trip = trips[0]
        assert "DepartTime" in trip
        assert "TripNumber" in trip


def test_fetch_trips_for_route_raises_exception_on_error():
    date_string = datetime.date.today().strftime("%m%d%Y")
    uri = trip_service.GO_API_TRIPS_URL.format(
        date_string=date_string, depart_station_code="A", arrival_station_code="B"
    )

    with requests_mock.Mocker() as m:
        m.get(uri, exc=Exception)
        with pytest.raises(exceptions.UnableToFetchTripsException):
            trip_service.fetch_trips_for_route("A", "B")
