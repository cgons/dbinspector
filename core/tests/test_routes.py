import datetime
from unittest import mock

import pytest
import requests_mock
import simplejson as json

import core.models as m
from core import exceptions
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


class TestDeleteRoute:
    def test_returns_500_on_failure(
        self, dbsession, users, stations, routes, userroutes
    ):
        dbsession.add_all(users + stations + routes)
        dbsession.flush()
        dbsession.add_all(userroutes)
        dbsession.commit()

        client = app.test_client()

        with mock.patch(
            "core.services.route_service.delete_user_route_association",
            side_effect=Exception,
        ):
            resp = client.delete("/portal/api/route/1/", headers={"X-USERID": "1"})

        assert resp.status_code == 500
        assert (
            json.loads(resp.data)["errors"]["system"]
            == "Sorry, unable to delete route due to system issues. Please try again."
        )
        assert dbsession.query(m.UserRoute).count() == 1

    def test_returns_200_on_success(
        self, dbsession, users, stations, routes, userroutes
    ):
        dbsession.add_all(users + stations + routes)
        dbsession.flush()
        dbsession.add_all(userroutes)
        dbsession.commit()

        client = app.test_client()
        resp = client.delete("/portal/api/route/1/", headers={"X-USERID": "1"})

        assert resp.status_code == 200
        assert dbsession.query(m.UserRoute).count() == 0


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

    def test_duplicate_route_not_created(self, dbsession, users, stations, routes):
        """Ensures that a duplicate route entry is not created if one already exists."""
        dbsession.add_all(users + stations + routes)
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
                headers={"X-USERID": "1"},                
            )
            assert resp.status_code == 200
            assert dbsession.query(m.Route).count() == 1

    def test_route_and_userroute_and_associated_trips_are_created(
        self, dbsession, stations, users
    ):
        """Ensures that a new route and new trips are created."""
        dbsession.add_all(stations + users)
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
                headers={"X-USERID": "1"},
            )

        assert resp.status_code == 200

        assert dbsession.query(m.Route).count() == 1
        assert dbsession.query(m.Trip).count() == 1
        assert dbsession.query(m.UserRoute).count() == 1

        # Ensure route created is associated with user.
        user_route = dbsession.query(m.UserRoute).first()
        assert user_route.user_id == 1
        assert user_route.route_id == 1

        # Ensure the trips are correctly associated.
        trip = dbsession.query(m.Trip).first()
        assert trip.trip_number == "101"
        assert trip.trip_time == "05:35"

    def test_existing_route_and_associated_trips_are_updated(
        self, dbsession, users, stations, routes, trips
    ):
        """Ensures that an existing route and associated trips are updated."""
        dbsession.add_all(users + stations + routes + trips)
        dbsession.commit()
        assert dbsession.query(m.Station).count() == 2
        assert dbsession.query(m.Route).count() == 1
        assert dbsession.query(m.Trip).count() == 1

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
                headers={"X-USERID": "1"},
            )

        assert resp.status_code == 200

        assert dbsession.query(m.Route).count() == 1
        assert dbsession.query(m.Trip).count() == 1

        # Ensure the trips are correctly associated.
        trip = dbsession.query(m.Trip).first()
        assert trip.trip_number == "101"
        assert trip.trip_time == "05:35"

    def test_returns_correct_error_msg_when_go_api_down(
        self, dbsession, stations, routes
    ):
        dbsession.add_all(stations + routes)
        dbsession.commit()
        assert dbsession.query(m.Station).count() == 2
        assert dbsession.query(m.Route).count() == 1

        client = app.test_client()
        post_data = {"depart_station_code": "A", "arrival_station_code": "B"}

        with mock.patch(
            "core.services.trip_service.fetch_trips_for_route",
            side_effect=exceptions.UnableToFetchTripsException,
        ):
            resp = client.post(
                "/portal/api/route/",
                data=json.dumps(post_data),
                content_type="application/json",
            )

        assert resp.status_code == 500
        assert (
            "GO Transit systems are offline"
            in json.loads(resp.data)["errors"]["system"]
        )
