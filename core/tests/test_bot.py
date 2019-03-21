import pytest
import requests_mock

from core import bot
from core import models as m


@pytest.fixture()
def mock_station_resp():
    return {
        "GetDepartStationsResult": {
            "Stations": [
                {"Code": "AC", "Name": "Acton GO"},
                {"Code": "UN", "Name": "Union GO"},
            ],
            "StatusCode": 200,
        }
    }


def test_populate_stations(dbsession, mock_station_resp):
    assert dbsession.query(m.Station).count() == 0

    with requests_mock.Mocker() as req_mock:
        req_mock.get(requests_mock.ANY, json=mock_station_resp)
        bot.populate_stations()

    assert dbsession.query(m.Station).count() == 2


def test_populate_stations_on_conflict(dbsession, mock_station_resp):
    # Insert two stations into the DB and then assert that they are not overwritten by
    # our FUC (which should not happen due to the use of SQLAlchemy's
    # insert.on_conflict_do_nothing)
    dbsession.add_all(
        [m.Station(code="AC", name="Action GO"), m.Station(code="UN", name="Union GO")]
    )
    dbsession.commit()
    assert dbsession.query(m.Station).count() == 2

    with requests_mock.Mocker() as req_mock:
        req_mock.get(requests_mock.ANY, json=mock_station_resp)
        bot.populate_stations()

    assert dbsession.query(m.Station).count() == 2


def test_fetch_stations():
    with requests_mock.Mocker() as req_mock:
        mock_resp = {
            "GetDepartStationsResult": {
                "Stations": [{"Code": "AC", "Name": "Acton GO"}],
                "StatusCode": 200,
            }
        }  # noqa
        req_mock.get(requests_mock.ANY, json=mock_resp)
        stations = bot.fetch_stations()

    assert stations == mock_resp["GetDepartStationsResult"]["Stations"]


def test_fetch_stations_returns_empty_list_on_exception():
    with requests_mock.Mocker() as req_mock:
        req_mock.get(requests_mock.ANY, exc=Exception)
        stations = bot.fetch_stations()

        assert stations == []


@pytest.mark.parametrize("result_type, expected", [(2, False), (1, True)])
def test_check_eligibility(result_type, expected):
    with requests_mock.Mocker() as req_mock:
        mock_resp = {
            "CheckEligibleResult": {
                "Reason": "",
                "ResultType": result_type,
                "StatusCode": 200,
            }
        }  # noqa
        req_mock.post(requests_mock.ANY, json=mock_resp)
        result = bot.check_eligibility(
            date_str="03082019", arrival_station_code="UN", trip_number="3806"
        )
        assert result is expected


def test_check_eligibility_returns_false_on_exception():
    with requests_mock.Mocker() as req_mock:
        req_mock.post(requests_mock.ANY, exc=Exception)
        result = bot.check_eligibility(
            date_str="03082019", arrival_station_code="UN", trip_number="3806"
        )
        assert result is False
