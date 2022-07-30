import os


def _get_config():
    configs = {
        "local": LocalConfig,
        "dev": DevelopmentConfig,
        "prod": ProductionConfig,
        "testing": TestingConfig,
    }
    return configs[os.environ.get("STAGE", "local")]()


class Config:
    SERVICE = os.environ["SERVICE"]
    LOGLEVEL = os.environ.get("LOGLEVEL", "INFO")
    ELASTICSEARCH_ENDPOINT = os.environ["ELASTICSEARCH_ENDPOINT"]
    API_VERSION = "v1"
    INDEX_NAME = os.environ["INDEX_NAME"]
    # https://github.com/flask-restful/flask-restful/issues/280
    PROPAGATE_EXCEPTIONS = True


class LocalConfig(Config):
    UNSAFE_ATTACH_DEBUGGER = True
    DEBUG = True
    DEVELOPMENT = True
    TESTING = False

    INDEX_SETTINGS = {"index": {"number_of_shards": 1, "number_of_replicas": 1}}
    INDEX_MAPPINGS = {
        "_meta": {"version": "v1"},
        "dynamic": "strict",
        "properties": {
            "type": {"type": "keyword"},
            "properties": {"dynamic": True, "type": "object"},
            "geo_shape": {"type": "keyword"},
            "geometry": {"type": "geo_shape"},
        },
    }
    SEED_DATA_LOCATION = os.environ["SEED_DATA_LOCATION"]


class DevelopmentConfig(Config):
    UNSAFE_ATTACH_DEBUGGER = True
    DEBUG = True
    DEVELOPMENT = True
    TESTING = False


class ProductionConfig(Config):
    UNSAFE_ATTACH_DEBUGGER = False
    TESTING = False
    DEBUG = False
    REJECT_HTTP = True


class TestingConfig(LocalConfig):
    TESTING = True


CONFIG = _get_config()
