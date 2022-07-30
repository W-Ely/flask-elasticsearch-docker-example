import elasticsearch.exceptions
import geojson
from flask_restful import Resource
from flask_restful.reqparse import RequestParser

import api.clients.es as es
from api.errors import ApiException
from api.logger import LOGGER
from api.types import wkt_type
from config import CONFIG


class Lines(Resource):
    def get(self):
        """
        Lines
        ---
        parameters:
         - in: query
           name: wkt
           type: string
           required: true
           description: Well-known text representation of a polygon
           default: POLYGON((-73.9795 40.7641,-73.9875 40.7550,-73.9788 40.7514,-73.9714 40.7610,-73.9795 40.7641))
        responses:
         200:
           description: GeoJson Feature Collection of line features that intesect with provided polygon
        """
        parser = RequestParser()
        parser.add_argument("wkt", type=wkt_type, required=True, nullable=False, trim=True)
        args = parser.parse_args()
        endpoint_filter = "LineString"
        LOGGER.debug("SHAPE", type=args.wkt["type"], coordinates=args.wkt["coordinates"])
        feature_collection = handle_query(endpoint_filter, args.wkt)
        return feature_collection, 200


class Points(Resource):
    def get(self):
        """
        Points
        ---
        parameters:
         - in: query
           name: wkt
           type: string
           required: true
           description: Well-known text representation of polygon
           default: POLYGON((-73.9795 40.7641,-73.9875 40.7550,-73.9788 40.7514,-73.9714 40.7610,-73.9795 40.7641))
        responses:
         200:
           description: GeoJson Feature Collection of point features that intesect with provided polygon
        """
        parser = RequestParser()
        parser.add_argument("wkt", type=wkt_type, required=True, nullable=False, trim=True)
        args = parser.parse_args()
        endpoint_filter = "Point"
        LOGGER.debug("SHAPE", type=args.wkt["type"], coordinates=args.wkt["coordinates"])
        feature_collection = handle_query(endpoint_filter, args.wkt)
        return feature_collection, 200


def handle_query(endpoint_filter, geo_shape):
    query = get_elasticsearch_query(endpoint_filter, geo_shape)
    try:
        elasticsearch_results = es.get_client().search(index=CONFIG.INDEX_NAME, body=query)
    except elasticsearch.exceptions.RequestError as re:
        # This isn't fool proof, but seems to get a human readable message from a RequestError.
        raise ApiException(
            f'Unsupported or invalid search: {re.info["error"]["root_cause"][0]["reason"]}', 400
        ) from re
    return collection_from_elasticsearch_results(elasticsearch_results)


def get_elasticsearch_query(endpoint_filter, geo_shape):
    return {
        "size": 10000,
        "_source": ["type", "geometry", "properties"],
        "query": {
            "bool": {
                "filter": [
                    {"term": {"geo_shape": endpoint_filter}},
                    {
                        "geo_shape": {
                            "geometry": {
                                "shape": {
                                    "type": geo_shape["type"],
                                    "coordinates": geo_shape["coordinates"],
                                },
                                "relation": "intersects",
                            }
                        }
                    },
                ],
            }
        },
    }


def collection_from_elasticsearch_results(elasticsearch_results):
    return geojson.GeoJSON({
        "type": "FeatureCollection",
        "features": [hit["_source"] for hit in elasticsearch_results["hits"]["hits"]],
    })
