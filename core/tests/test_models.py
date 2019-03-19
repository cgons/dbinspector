from core import models as m
from tests.conftest import DBInspector


class TestStation:
    def test_get_stations(self, dbsession, stations):
        assert dbsession.query(m.Station).count() == 0

        dbsession.add_all(stations)
        dbsession.commit()

        stations = m.Station.get_stations(dbsession)
        assert len(stations) == 2

    def test_get_stations_with_filter(self, dbsession, stations):
        assert dbsession.query(m.Station).count() == 0

        dbsession.add_all(stations)
        dbsession.commit()

        filter_exp = (m.Station.code == "B")
        stations = m.Station.get_stations(dbsession, filter_exp)

        assert len(stations) == 1


class TestRoute:
    def test_serialize(self, dbsession, stations, routes, trips):
        assert dbsession.query(m.Station).count() == 0
        assert dbsession.query(m.Route).count() == 0
        assert dbsession.query(m.Trip).count() == 0

        dbsession.add_all(stations + routes + trips)
        dbsession.commit()

        with DBInspector(dbsession.connection()) as inspector:
            route = dbsession.query(m.Route).first()
            assert route.serialize() == {
                'depart_station': 'Station A',
                'depart_station_code': 'A',
                'arrival_station': 'Station B',
                'arrival_station_code': 'B',
                'trips': [{'trip_number': '101', 'trip_time': '05:35'}]
            }
            assert inspector.get_count() == 2
