"""Implementation of API operations on cases."""

import typing
import uuid

import requests
from logzero import logger

from .models import Case, CONVERTER

#: End point for listing cases.
ENDPOINT_CASE_LIST = "/variants/api/case/{project_uuid}/"


def case_list(
    server_url: str, api_key: str, project_uuid: typing.Union[str, uuid.UUID]
) -> typing.List[Case]:
    """Listing of cases from a project UUID."""
    while server_url.endswith("/"):
        server_url = server_url[:-1]
    endpoint = "%s%s" % (server_url, ENDPOINT_CASE_LIST.format(project_uuid=project_uuid))
    logger.debug("Sending request to end point %s", endpoint)
    headers = {"Authorization": "Bearer %s" % api_key}
    result = requests.get(endpoint, headers=headers)
    result.raise_for_status()
    return CONVERTER.structure(result.json(), typing.List[Case])
