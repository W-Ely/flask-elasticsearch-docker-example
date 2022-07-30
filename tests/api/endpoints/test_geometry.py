import pytest

from api.endpoints.geometry import (
    collection_from_elasticsearch_results,
    get_elasticsearch_query,
)


@pytest.mark.parametrize(
    "wkt, expected_result_count, msg",
    [
        (
            "POLYGON((-122.3856 47.5853,-122.2778 47.5853,-122.2778 47.6223,-122.3856 47.6223,-122.3856 47.5853))",
            0,
            "1) Polygon intersects 0 lines",
        ),
        (
            "POLYGON((-122.4824 47.5357,-122.1981 47.5357,-122.1981 47.7060,-122.4824 47.7060,-122.4824 47.5357))",
            4,
            "2) Polygon intersects 4 lines",
        ),
        (
            "POLYGON((-122.4893 47.7097,-122.4872 47.6672,-122.1700 47.6727,-122.1659 47.7097,-122.4893 47.7097))",
            1,
            "3) Polygon intersects 1 line",
        ),
        (
            "POLYGON((-122.3513 47.6431, -122.3011 47.6431, -122.3011 47.7416, -122.3513 47.7416, -122.3513 47.6431))",
            1,
            "4) Polygon intersects 1 line",
        ),
        (  # This is an odd test but I suppose technically this line being the same deosn't intersect itself.
            "LINESTRING(-122.3286 47.7310,-122.3265 47.6556)",
            0,
            "5)LineString *is* 1 line",
        ),
        ("LINESTRING(-122.3602 47.6991,-122.2922 47.7000)", 1, "6) LineString intersects 1 line",),
        (
            "POLYGON((-122.4975 47.6861,-122.3822 47.6117,-122.4906 47.5440,-122.4474 47.5185,-122.3286 47.5890,-122.2373 47.5311,-122.2043 47.5589,-122.2881 47.6029,-122.1851 47.6949,-122.2242 47.7102,-122.3252 47.6293,-122.4508 47.7116,-122.4975 47.6861))",
            0,
            "7) Polygon intersects 0 lines",
        ),
    ],
)
def test_lines_get_200(flask_client, es_client, wkt, expected_result_count, msg):
    response = flask_client.get(f"v1/lines?wkt={wkt}")
    assert response.status_code == 200, msg
    assert len(response.json["features"]) == expected_result_count, msg


@pytest.mark.parametrize(
    "wkt_query_string, msg",
    [
        (
            "?wkt=POLYGON((-122.4927 47.7568,-122.4453 47.7190,-122.4927 47.7568,-122.4419 47.7591,-122.4879 47.7245))",
            "1) Polygon Malformed: Caught by elasticsearch",
        ),
        (
            "?wkt=TRIANGLE((-122.3856 47.5853,-122.2778 47.6223,-122.2778 47.5853))",
            "2) Polygon Unsupported: Caught by parser",
        ),
        ("", "3) No query query string",),
    ],
)
def test_lines_invalid_polygon_search_400(flask_client, es_client, wkt_query_string, msg):
    response = flask_client.get(f"v1/lines{wkt_query_string}")
    assert response.status_code == 400, msg


@pytest.mark.parametrize(
    "wkt, expected_result_count, msg",
    [
        (
            "POLYGON((-122.3856 47.5853,-122.2778 47.5853,-122.2778 47.6223,-122.3856 47.6223,-122.3856 47.5853))",
            0,
            "1) Polygon intersects 0 points",
        ),
        (
            "POLYGON((-122.4824 47.5357,-122.1981 47.5357,-122.1981 47.7060,-122.4824 47.7060,-122.4824 47.5357))",
            8,
            "2) Polygon intersects 8 points",
        ),
        (
            "POLYGON((-122.4893 47.7097,-122.4872 47.6672,-122.1700 47.6727,-122.1659 47.7097,-122.4893 47.7097))",
            2,
            "3) Polygon intersects 2 points",
        ),
        (
            "POLYGON((-122.3513 47.6431, -122.3011 47.6431, -122.3011 47.7416, -122.3513 47.7416, -122.3513 47.6431))",
            0,
            "4) Polygon intersects 0 points",
        ),
        ("LINESTRING(-122.3286 47.7310,-122.3265 47.6556)", 0, "5) LineString intersects 0 points",),
        ("LINESTRING(-122.3602 47.6991,-122.2922 47.7000)", 0, "6) LineString intersects 0 points",),
        (
            "POLYGON((-122.4975 47.6861,-122.3822 47.6117,-122.4906 47.5440,-122.4474 47.5185,-122.3286 47.5890,-122.2373 47.5311,-122.2043 47.5589,-122.2881 47.6029,-122.1851 47.6949,-122.2242 47.7102,-122.3252 47.6293,-122.4508 47.7116,-122.4975 47.6861))",
            8,
            "7) Polygon intersects 8 points",
        ),
    ],
)
def test_points_get_200(flask_client, es_client, wkt, expected_result_count, msg):
    response = flask_client.get(f"v1/points?wkt={wkt}")
    assert response.status_code == 200, msg
    assert len(response.json["features"]) == expected_result_count, msg


@pytest.mark.parametrize(
    "wkt_query_string, msg",
    [
        (
            "?wkt=POLYGON((-122.4927 47.7568,-122.4453 47.7190,-122.4927 47.7568,-122.4419 47.7591,-122.4879 47.7245))",
            "1) Polygon Malformed: Caught by elasticsearch",
        ),
        (
            "?wkt=TRIANGLE((-122.3856 47.5853,-122.2778 47.6223,-122.2778 47.5853))",
            "2) Polygon Unsupported: Caught by parser",
        ),
        ("", "3) No query query string",),
    ],
)
def test_points_invalid_polygon_search_400(flask_client, es_client, wkt_query_string, msg):
    response = flask_client.get(f"v1/points{wkt_query_string}")
    assert response.status_code == 400, msg


def test_get_elasticsearch_query():
    endpoint_filter = "LineString"
    geo_shape = {"type": "Polygon", "coordinates": [0.0]}
    expected = {
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
    actual = get_elasticsearch_query(endpoint_filter, geo_shape)
    assert actual == expected


def test_collection_from_elasticsearch_results():
    mock_es_results = {
        "hits": {
            "hits": [
                {
                    "_id": "xvgmcHMB-SNv9PG8Qr8A",
                    "_source": {
                        "geometry": {
                            "coordinates": [[-122.3286, 47.731], [-122.3265, 47.6556]],
                            "type": "LineString",
                        },
                        "type": "Feature",
                        "properties": {},
                    },
                }
                for _ in range(25)
            ]
        }
    }
    expected = {
        "type": "FeatureCollection",
        "features": [
            {
                "geometry": {
                    "coordinates": [[-122.3286, 47.731], [-122.3265, 47.6556]],
                    "type": "LineString",
                },
                "type": "Feature",
                "properties": {},
            }
            for _ in range(25)
        ],
    }
    actual = collection_from_elasticsearch_results(mock_es_results)
    assert actual == expected
