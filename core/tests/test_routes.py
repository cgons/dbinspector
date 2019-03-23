import datetime
from unittest import mock

import pytest
import requests_mock
import simplejson as json

import core.models as m
from core.application import app
from core.services import trip_service


def test_get_stations(dbsession, stations):
    dbsession.add_all(stations)
    dbsession.commit()

    client = app.test_client()
    resp = client.get("/portal/api/get-stations/")
    print(resp)


# Route Endpoint Test Cases
# ------------------------------------------------------------------------------------------
def test_get_route(dbsession, stations, routes, trips):
    dbsession.add_all(stations + routes + trips)
    dbsession.commit()

    client = app.test_client()
    resp = client.get("/portal/api/route/1/")

    assert resp.json == {
        "arrival_station": "Station B",
        "arrival_station_code": "B",
        "depart_station": "Station A",
        "depart_station_code": "A",
        "trips": [{"trip_number": "101", "trip_time": "05:35"}],
    }


class TestCreateRoute:
    def test_returns_400_on_int_station_code(self, dbsession):
        """Ensure 400 response + error message when invalid station code provided."""
        client = app.test_client()
        post_data = {"depart_station_code": "A", "arrival_station_code": 123}
        resp = client.post(
            "/portal/api/route/",
            data=json.dumps(post_data),
            content_type="application/json",
        )

        assert resp.status_code == 400  # Bad Request

        resp_json = resp.get_json()
        assert "arrival_station_code" in resp_json["errors"]

        # Ensure no Route entry was created...
        assert dbsession.query(m.Route).count() == 0

    def test_returns_400_on_missing_input(self, dbsession):
        """Ensure 400 response + error message when invalid station code provided."""
        client = app.test_client()
        post_data = {"depart_station_code": "A"}
        resp = client.post(
            "/portal/api/route/",
            data=json.dumps(post_data),
            content_type="application/json",
        )

        assert resp.status_code == 400  # Bad Request

        resp_json = resp.get_json()
        assert "arrival_station_code" in resp_json["errors"]

        # Ensure no Route entry was created...
        assert dbsession.query(m.Route).count() == 0

    def test_duplicate_route_not_created(self, dbsession, stations, routes):
        """Ensures that a duplicate route entry is not created if one already exists."""
        dbsession.add_all(stations + routes)
        dbsession.commit()
        assert dbsession.query(m.Route).count() == 1

        with mock.patch("core.services.trip_service.fetch_trips_for_route"), mock.patch(
            "core.services.trip_service.insert_trips_for_route"
        ):
            client = app.test_client()
            post_data = {"depart_station_code": "A", "arrival_station_code": "B"}
            resp = client.post(
                "/portal/api/route/",
                data=json.dumps(post_data),
                content_type="application/json",
            )
            assert resp.status_code == 200
            assert dbsession.query(m.Route).count() == 1

    def test_route_and_associated_trips_are_created(self, dbsession, stations):
        """Ensures that a new route and new trips are created."""
        dbsession.add_all(stations)
        dbsession.commit()
        assert dbsession.query(m.Route).count() == 0
        assert dbsession.query(m.Trip).count() == 0

        client = app.test_client()
        post_data = {"depart_station_code": "A", "arrival_station_code": "B"}

        mock_trips = [{"TripNumber": "101", "DepartTime": "05:35"}]
        with mock.patch(
            "core.services.trip_service.fetch_trips_for_route", return_value=mock_trips
        ):
            resp = client.post(
                "/portal/api/route/",
                data=json.dumps(post_data),
                content_type="application/json",
            )

        assert resp.status_code == 200

        assert dbsession.query(m.Route).count() == 1
        assert dbsession.query(m.Trip).count() == 1

        # Ensure the trips are correctly associated.
        trip = dbsession.query(m.Trip).first()
        assert trip.trip_number == "101"
        assert trip.trip_time == "05:35"

    @pytest.mark.skip
    def test_existing_route_and_associated_trips_are_updated(
        self, dbsession, stations, routes, trips
    ):
        """Ensures that an existing route and associated trips are updated."""
        dbsession.add_all(stations + routes + trips)
        dbsession.commit()

        assert dbsession.query(m.Route).count() == 1
        assert dbsession.query(m.Trip).count() == 1

        client = app.test_client()
        post_data = {"depart_station_code": "A", "arrival_station_code": "B"}
        resp = client.post(
            "/portal/api/route/",
            data=json.dumps(post_data),
            content_type="application/json",
        )

        assert resp.status_code == 200

        assert dbsession.query(m.Route).count() == 1
        assert dbsession.query(m.Trip).count() == 1

        # Ensure the trips are correctly associated.
        trip = dbsession.query(m.Trip).first()
        assert trip.depart_station_code == "A"
        assert trip.arrival_station_code == "B"
        assert trip.trip_number == "101"
        assert trip.trip_time == "05:35"

    @pytest.mark.skip
    def test_updates_existing_route_and_inserts_new_trip(
        self, dbsession, stations, routes, trips
    ):
        """Ensures that an existing route is updated and a new trip is inserted."""
        dbsession.add_all(stations + routes + trips)
        dbsession.commit()

        assert dbsession.query(m.Route).count() == 1
        assert dbsession.query(m.Trip).count() == 1

        client = app.test_client()
        post_data = {"depart_station_code": "A", "arrival_station_code": "B"}
        resp = client.post(
            "/portal/api/route/",
            data=json.dumps(post_data),
            content_type="application/json",
        )

        assert resp.status_code == 200

        assert dbsession.query(m.Route).count() == 1
        assert dbsession.query(m.Trip).count() == 2

        # Ensure the trips are correctly associated.
        trip_101 = dbsession.query(m.Trip).get("101")
        assert trip_101.depart_station_code == "A"
        assert trip_101.arrival_station_code == "B"
        assert trip_101.trip_number == "101"
        assert trip_101.trip_time == "05:35"

        trip_102 = dbsession.query(m.Trip).get("102")
        assert trip_102.depart_station_code == "A"
        assert trip_102.arrival_station_code == "B"
        assert trip_102.trip_number == "102"
        assert trip_102.trip_time == "05:45"
