import logging
import os
import sys

import geojson
from elasticsearch import Elasticsearch, ConnectionError

from config import CONFIG

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(os.environ["LOGLEVEL"])
LOGGER.addHandler(logging.StreamHandler(stream=sys.stderr))

_CLIENT = None


def get_es_client():
    global _CLIENT
    if not _CLIENT:
        _CLIENT = Elasticsearch(CONFIG.ELASTICSEARCH_ENDPOINT)
    return _CLIENT


def wait_healthy(es):
    LOGGER.debug("Waiting for Elasticsearch health")
    es_healthy = False
    while not es_healthy:
        try:
            health = es.cluster.health(wait_for_status="yellow", request_timeout=10)
            es_healthy = True if health.get("status") in {"yellow", "green"} else False
            LOGGER.debug(f'Health status: {health.get("status")}')
        except ConnectionError:
            pass


def configure_cluster(es):
    LOGGER.debug("Configuring cluster")
    es.cluster.put_settings(body={"persistent": {"action.auto_create_index": False}})


def clean_cluster(es, index_name):
    LOGGER.debug("Cleaning cluster")
    es.indices.delete(index_name, ignore=404)


def create_index(es, index_name, mappings, settings):
    LOGGER.debug("Creating index")
    body = {"mappings": mappings, "settings": settings}
    es.indices.create(index=index_name, body=body)


def get_features(geojson_location):
    LOGGER.debug("Getting features")
    with open(geojson_location, "r") as geojson_file:
        geo_data = geojson.load(geojson_file)
    return geo_data


def populate_index(es, features, index_name):
    for feature in features:
        # Adding this non-standard field for filtering on in elasticsearch.
        feature["geo_shape"] = feature["geometry"]["type"]
        es.index(index=index_name, body=feature, refresh=True)


def search(es=None, geojson_location=CONFIG.SEED_DATA_LOCATION):
    LOGGER.debug("Seeding search")
    if not es:
        es = get_es_client()
    wait_healthy(es)
    configure_cluster(es)
    clean_cluster(es, CONFIG.INDEX_NAME)
    create_index(es, CONFIG.INDEX_NAME, CONFIG.INDEX_MAPPINGS, CONFIG.INDEX_SETTINGS)
    feature_collection = get_features(geojson_location)
    populate_index(es, feature_collection["features"], CONFIG.INDEX_NAME)
