import functools
import logging

import marshmallow
from flask import jsonify, request, g

from core import exceptions, models as m, validators
from core.application import app, session
from core.services import route_service


log = logging.getLogger(__name__)


# Utils
# --------------------------------------------------------------------------------------
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


@app.before_request
def before_req():
    # Set current user
    g.user_id = request.headers.get("X-USERID", None)


# Endpoints
# --------------------------------------------------------------------------------------
@app.route("/portal/api/get-stations/")
def get_stations():
    """Returns a list of stations stored in the DB"""
    return jsonify(m.Station.get_stations(session))


# Route
# -----------------
@app.route("/portal/api/route/<int:route_id>/", methods=["GET"])
def get_route(route_id):
    route = session.query(m.Route).get(route_id)
    return jsonify(route.serialize())


@app.route("/portal/api/route/", methods=["POST"])
def create_route():
    status_code = 200
    resp = {"content": {}, "errors": {}}
    post_data = request.get_json()

    try:
        route_info = validators.RouteSchema(strict=True).load(post_data).data
        route_service.create_route_and_associated_trips(session, route_info, g.user_id)
    except marshmallow.exceptions.ValidationError as e:
        resp["errors"] = e.messages
        status_code = 400
    except exceptions.UnableToFetchTripsException:
        dsc = route_info["depart_station_code"]
        asc = route_info["arrival_station_code"]
        log.exception("Unable to fetch Trips from GO API for route: {dsc} - {asc}")
        msg = (
            "Sorry, looks like the GO Transit systems are offline right now. "
            + "Please try again soon."
        )
        resp["errors"]["system"] = msg
        status_code = 500
    return jsonify(resp), status_code


@app.route("/portal/api/route/<int:route_id>/", methods=["DELETE"])
def delete_route(route_id):
    """This endpoint is responsible for deleting the User -> Route association only."""
    status_code = 200
    resp = {"content": {}, "errors": {}}

    try:
        route_service.delete_user_route_association(session, g.user_id, route_id)
    except:
        status_code = 500
        msg = "Sorry, unable to delete route due to system issues. Please try again."
        resp["errors"]["system"] = msg

    return jsonify(resp), status_code


# -----------------
