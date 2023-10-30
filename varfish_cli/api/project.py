"""Implementation of API operations on cases."""

import typing
import uuid

from logzero import logger
import requests

from varfish_cli.api.models import CONVERTER, Project
from varfish_cli.api.varannos import raise_for_status
from varfish_cli.common import strip_trailing_slash

ACCEPT_API_VARFISH = ""

#: End point for listing projects.
ENDPOINT_PROJECT_LIST = "/project/api/list"
#: End point for retrieving projects.
ENDPOINT_PROJECT_RETRIEVE = "/project/api/retrieve/{project_uuid}"


def project_list(
    server_url: str,
    api_token: str,
    verify_ssl: bool = True,
) -> typing.List[Project]:
    """Listing of all projects that a user has access to."""
    server_url = strip_trailing_slash(server_url)
    endpoint = f"{server_url}{ENDPOINT_PROJECT_LIST}"
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    raise_for_status(result)
    return CONVERTER.structure(result.json(), typing.List[Project])


def project_retrieve(
    server_url: str,
    api_token: str,
    project_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> typing.List[Project]:
    """Listing of all projects that a user has access to."""
    server_url = strip_trailing_slash(server_url)
    endpoint = f"{server_url}{ENDPOINT_PROJECT_RETRIEVE}".format(project_uuid=project_uuid)
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    raise_for_status(result)
    return CONVERTER.structure(result.json(), Project)
