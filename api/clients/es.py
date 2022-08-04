from elasticsearch import Elasticsearch

from config import CONFIG

_CLIENT = None


def get_client():
    global _CLIENT
    if not _CLIENT:
        _CLIENT = Elasticsearch(CONFIG.ELASTICSEARCH_ENDPOINT)
    return _CLIENT
