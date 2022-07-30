import pytest

import seed
from api import create_app
from config import CONFIG


@pytest.fixture(scope="session")
def flask_client():
    app = create_app(CONFIG)
    with app.test_request_context("/"):
        yield app.test_client()


@pytest.fixture()
def es_client():
    es = seed.get_es_client()
    seed.search(es=es, geojson_location="./tests/mock_data/simple.geojson")
    yield es

    seed.clean_cluster(es, CONFIG.INDEX_NAME)


def pytest_assertrepr_compare(config, op, left, right):
    """
    Override pytest default print behaviour with hook to not truncate diffrences at all

    Has the side effect of not showing where the differeneces are, but still better for building
    out tests.  Consider removing once most tests are written.
    """
    if op in ("==", "!=", "is", "in"):
        return ["{0} {1} {2}".format(left, op, right)]
