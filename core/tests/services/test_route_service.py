from unittest import mock

import pytest

from core.services import route_service
from core import models as m


def test_create_route_and_associated_trips_results_in_no_change_when_route_insert_fails(
    dbsession, users, stations
):
    dbsession.add_all(users + stations)
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
    
    with pytest.raises(Exception):
        route_service.create_route_and_associated_trips(
            mock_dbsession, route_info, user_id=1
        )

        assert dbsession.query(m.Route).count() == 0
        assert dbsession.query(m.Trip).count() == 0
