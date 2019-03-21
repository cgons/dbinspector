from unittest import mock

from core.services import route_service
from core import models as m


def test_create_route_and_associated_trips_results_in_no_change_when_route_insert_fails(
    dbsession, stations
):
    dbsession.add_all(stations)
    dbsession.commit()

    assert dbsession.query(m.Route).count() == 0
    assert dbsession.query(m.Trip).count() == 0

    mock_dbsession = mock.Mock()
    mock_dbsession.connection.side_effect = Exception
    route_info = {
        "depart_station_code": "A",
        "arrival_station_code": "B",
        "trips": [
            {"trip_number": "101", "trip_time": "05:35"},
            {"trip_number": "102", "trip_time": "05:45"},
        ],
    }
    route_service.create_route_and_associated_trips(mock_dbsession, route_info)

    assert dbsession.query(m.Route).count() == 0
    assert dbsession.query(m.Trip).count() == 0
