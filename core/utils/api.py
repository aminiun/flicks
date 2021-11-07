import requests

from core.exceptions import ApiCallException


class ApiCall:

    @staticmethod
    def api_call(method: str, url: str, expected_status: int, data: dict = None) -> requests.Response:
        # try:
        res = requests.request(
            method=method,
            url=url,
            json=data
        )
        # except (ConnectionError, InvalidShema)
        if res.status_code != expected_status:
            # TODO logging
            raise ApiCallException(
                f"Failed to get response from api {url} "
                f"Expected status {expected_status}"
            )

        return res
