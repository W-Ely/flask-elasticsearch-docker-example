from contextlib import nullcontext as does_not_raise

import pytest

from api import types


@pytest.mark.parametrize(
    "input, expected, context, msg",
    [
        (
            "POLYGON((-122.48931884765626 47.70976154266637,-122.4872589111328 47.66723703450518,-122.17002868652344 47.67278567576541,-122.16590881347656 47.70976154266637,-122.48931884765626 47.70976154266637))",
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-122.48931884765626, 47.70976154266637],
                        [-122.4872589111328, 47.66723703450518],
                        [-122.17002868652344, 47.67278567576541],
                        [-122.16590881347656, 47.70976154266637],
                        [-122.48931884765626, 47.70976154266637],
                    ]
                ],
            },
            does_not_raise(),
            "1) Basic Polygon",
        ),
        (
            "LINESTRING(-122.48931884765626 47.70976154266637,-122.4872589111328 47.66723703450518,-122.17002868652344 47.67278567576541)",
            {
                "type": "LineString",
                "coordinates": [
                    [-122.48931884765626, 47.70976154266637],
                    [-122.4872589111328, 47.66723703450518],
                    [-122.17002868652344, 47.67278567576541],
                ],
            },
            does_not_raise(),
            "2) Basic LineString",
        ),
        (
            "TRIANGLE((-122.48931884765626 47.70976154266637,-122.4872589111328 47.66723703450518,-122.17002868652344 47.67278567576541,-122.48931884765626 47.70976154266637))",
            None,
            pytest.raises(ValueError),
            "3) Unsupported Shape: Triangle",
        ),
        ("GARBAGE(oscar)", None, pytest.raises(ValueError), "Unsupported Garbage",),
    ],
)
def test_wkt_type(input, expected, context, msg):
    with context:
        assert types.wkt_type(input) == expected, msg
