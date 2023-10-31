from varfish_cli.exceptions import RestApiCallException


def raise_for_status(response):
    if not response.ok:  # pragma: no cover
        raise RestApiCallException(f"Problem with API call: {response.text}.")
