from json import JSONDecodeError

from simplejson import JSONDecodeError as SimpleJSONDecodeError

from varfish_cli.exceptions import RestApiCallException


def raise_for_status(response):
    if not response.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                response.status_code,
                " ".join([" ".join(v) for v in response.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (response.status_code, response.content)
        raise RestApiCallException(msg)
