import pytest

from api.errors import ApiException


def test_api_exception():
    api_exception = ApiException("Oops", 808)
    assert api_exception.error == "Oops"
    assert api_exception.status == 808
    with pytest.raises(ApiException):
        raise api_exception
