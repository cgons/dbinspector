from core import models as m
from core.services import trip_service


def test_insert_trips_for_route(dbsession, stations, routes):
    """Ensure trips are inserted correctly (with leading/trailing whitespace removed)."""
    dbsession.add_all(stations + routes)
    dbsession.commit()

    assert dbsession.query(m.Trip).count() == 0

    trips = [dict(trip_number="   102", trip_time="05:45   ")]
    trip_service.insert_trips_for_route(dbsession, "A", "B", trips)

    trips = dbsession.query(m.Trip).all()
    assert len(trips) == 1

    trip = trips[0]
    assert trip.depart_station_code == "A"
    assert trip.arrival_station_code == "B"
    assert trip.trip_number == "102"
    assert trip.trip_time == "05:45"


def test_insert_trips_for_route_updates_trip(dbsession, stations, routes, trips):
    """Ensure trips are inserted correctly (with leading/trailing whitespace removed)."""
    dbsession.add_all(stations + routes + trips)
    dbsession.commit()

    assert dbsession.query(m.Trip).count() == 1

    trips = [dict(trip_number="101", trip_time="05:55")]
    trip_service.insert_trips_for_route(dbsession, "A", "B", trips)

    trips = dbsession.query(m.Trip).all()
    assert len(trips) == 1

    trip = trips[0]
    assert trip.depart_station_code == "A"
    assert trip.arrival_station_code == "B"
    assert trip.trip_number == "101"
    assert trip.trip_time == "05:55"
