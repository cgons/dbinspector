import simplejson as json

import core.models as m
from core.application import app


# Route Endpoint Test Cases
# ------------------------------------------------------------------------------------------
def test_get_route(dbsession, stations, routes, trips):
    dbsession.add_all(stations + routes + trips)
    dbsession.commit()

    client = app.test_client()
    resp = client.get("/portal/api/route/A-B/")

    assert resp.json == {
        'arrival_station': 'Station B',
        'arrival_station_code': 'B',
        'depart_station': 'Station A',
        'depart_station_code': 'A',
        'trips': [{'trip_number': '101', 'trip_time': '05:35'}]
    }


class TestCreateRoute:
    def test_returns_400_on_int_station_code(self, dbsession):
        """Ensure 400 response + error message when invalid station code provided."""
        client = app.test_client()
        post_data = {
            "depart_station_code": "A",
            "arrival_station_code": 123,
            "trips": [
                {'trip_number': '101', 'trip_time': '05:35'},
                {'trip_number': '102', 'trip_time': '06:12'}
            ]
        }
        resp = client.post(
            "/portal/api/route/",
            data=json.dumps(post_data),
            content_type="application/json"
        )

        assert resp.status_code == 400  # Bad Request

        resp_json = resp.get_json()
        assert "arrival_station_code" in resp_json["errors"]

        # Ensure no Route entry was created...
        assert dbsession.query(m.Route).count() == 0

    def test_returns_400_on_missing_input(self, dbsession):
        """Ensure 400 response + error message when invalid station code provided."""
        client = app.test_client()
        post_data = {
            "depart_station_code": "A",
            "trips": [
                {'trip_number': '101', 'trip_time': '05:35'},
                {'trip_number': '102', 'trip_time': '06:12'}
            ]
        }
        resp = client.post(
            "/portal/api/route/",
            data=json.dumps(post_data),
            content_type="application/json"
        )

        assert resp.status_code == 400  # Bad Request

        resp_json = resp.get_json()
        assert "arrival_station_code" in resp_json["errors"]

        # Ensure no Route entry was created...
        assert dbsession.query(m.Route).count() == 0

    def test_returns_400_on_empty_trips(self, dbsession):
        """Ensure 400 response + error message when invalid station code provided."""
        client = app.test_client()
        post_data = {
            "depart_station_code": "A",
            "arrival_station_code": "B",
        }
        resp = client.post(
            "/portal/api/route/",
            data=json.dumps(post_data),
            content_type="application/json"
        )

        assert resp.status_code == 400  # Bad Request

        resp_json = resp.get_json()
        assert "trips" in resp_json["errors"]

        # Ensure no Route entry was created...
        assert dbsession.query(m.Route).count() == 0

    def test_returns_400_on_invalid_trip_schema(self, dbsession):
        """Ensure 400 response + error message when invalid station code provided."""
        client = app.test_client()
        post_data = {
            "depart_station_code": "A",
            "arrival_station_code": "B",
            "trips": [
                {'trip_number': '101', 'trip_time': '05:35'},
                {'trip_number': '102'}
            ]
        }
        resp = client.post(
            "/portal/api/route/",
            data=json.dumps(post_data),
            content_type="application/json"
        )

        assert resp.status_code == 400  # Bad Request

        resp_json = resp.get_json()
        assert "trip_time" in resp_json["errors"]["trips"]["1"]

        # Ensure no Route entry was created...
        assert dbsession.query(m.Route).count() == 0

    def test_route_and_associated_trips_are_created(self, dbsession, stations):
        """Ensures that a new route and new trips are created."""
        dbsession.add_all(stations)
        dbsession.commit()

        assert dbsession.query(m.Route).count() == 0
        assert dbsession.query(m.Trip).count() == 0

        client = app.test_client()
        post_data = {
            "depart_station_code": "A",
            "arrival_station_code": "B",
            "trips": [
                {"trip_number": "110", "trip_time": "09:30"},
                {"trip_number": "111", "trip_time": "10:30"},
            ]
        }
        resp = client.post(
            "/portal/api/route/",
            data=json.dumps(post_data),
            content_type="application/json"
        )

        assert resp.status_code == 200

        assert dbsession.query(m.Route).count() == 1
        assert dbsession.query(m.Trip).count() == 2

        # Ensure the trips are correctly associated.
        trips = dbsession.query(m.Trip).all()
        for t in trips:
            assert t.depart_station_code == "A"
            assert t.arrival_station_code == "B"

    def test_existing_route_and_associated_trips_are_updated(
        self, dbsession, stations, routes, trips
    ):
        """Ensures that an existing route and associated trips are updated."""
        dbsession.add_all(stations + routes + trips)
        dbsession.commit()

        assert dbsession.query(m.Route).count() == 1
        assert dbsession.query(m.Trip).count() == 1

        client = app.test_client()
        post_data = {
            "depart_station_code": "A",
            "arrival_station_code": "B",
            "trips": [
                {"trip_number": "101", "trip_time": "05:35"},
            ]
        }
        resp = client.post(
            "/portal/api/route/",
            data=json.dumps(post_data),
            content_type="application/json"
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

    def test_updates_existing_route_and_inserts_new_trip(
        self, dbsession, stations, routes, trips
    ):
        """Ensures that an existing route is updated and a new trip is inserted."""
        dbsession.add_all(stations + routes + trips)
        dbsession.commit()

        assert dbsession.query(m.Route).count() == 1
        assert dbsession.query(m.Trip).count() == 1

        client = app.test_client()
        post_data = {
            "depart_station_code": "A",
            "arrival_station_code": "B",
            "trips": [
                {"trip_number": "101", "trip_time": "05:35"},
                {"trip_number": "102", "trip_time": "05:45"},
            ]
        }
        resp = client.post(
            "/portal/api/route/",
            data=json.dumps(post_data),
            content_type="application/json"
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
