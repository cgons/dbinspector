from marshmallow import Schema, fields


class RouteSchema(Schema):
    depart_station_code = fields.Str(required=True)
    arrival_station_code = fields.Str(required=True)
