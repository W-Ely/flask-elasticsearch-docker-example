import flask_restful
from flask import Blueprint

from api.endpoints import geometry as geometry
from config import CONFIG

blueprint = Blueprint("api", __name__)
api = flask_restful.Api(blueprint, prefix=f"/{CONFIG.API_VERSION}")

api.add_resource(geometry.Lines, "/lines")
api.add_resource(geometry.Points, "/points")
