import functools
import logging

import marshmallow
from flask import jsonify, request

from core.application import app, session
from . import models as m
from . import validators
from .services import route_service


log = logging.getLogger(__name__)


# Utils
# ------------------------------------------------------------------------------------------
def private_key_required(fn):
    """Marks a route as a private/internal/system route.
    Will only be processed if Authorization token (ie. private key) matches.
    """
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        if request.headers.get("Authorization") != app.config["SECRET_KEY"]:
            return "Unauthorized", 401
        return fn(*args, **kwargs)
    return wrapped


# Endpoints
# ------------------------------------------------------------------------------------------
@app.route("/portal/api/get-stations/")
def get_stations():
    """Returns a list of stations stored in the DB"""
    return jsonify(m.Station.get_stations())


# Route
# -----------------
@app.route(
    "/portal/api/route/<string:depart_station_code>-<string:arrival_station_code>/",
    methods=["GET"]
)
def get_route(depart_station_code, arrival_station_code):
    route = session.query(m.Route).get([depart_station_code, arrival_station_code])
    return jsonify(route.serialize())


@app.route("/portal/api/route/", methods=["POST"])
def create_route():
    resp = {"content": {}, "errors": {}}
    post_data = request.get_json()

    try:
        route_info = validators.RouteSchema(strict=True).load(post_data).data
        route_service.create_route_and_associated_trips(session, route_info)
    except marshmallow.exceptions.ValidationError as e:
        resp["errors"] = e.messages
        return jsonify(resp), 400
    return jsonify(resp)


@app.route("/portal/api/route/<id>/", methods=["PUT"])
def update_route():
    pass


@app.route("/portal/api/route/<id>/", methods=["DELETE"])
def delete_route():
    pass
# -----------------
