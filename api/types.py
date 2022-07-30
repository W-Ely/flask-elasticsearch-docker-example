import geojson
from geomet import wkt

from api.logger import LOGGER


def wkt_type(input):
    try:
        output = wkt.loads(input)
        geojson.GeoJSON(output)
    except Exception:
        LOGGER.debug("Validation Error", exc_info=True)
        raise ValueError("Invalid or unsupported wkt")
    return output
