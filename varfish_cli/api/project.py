"""Implementation of API operations on cases."""

import typing
import uuid

from logzero import logger
import pydantic
import requests

from varfish_cli.api.common import raise_for_status
from varfish_cli.api.models import Project, SettingsEntry
from varfish_cli.common import strip_trailing_slash

ACCEPT_API_VARFISH = ""

#: End point for listing projects.
ENDPOINT_PROJECT_LIST = "/project/api/list"
#: End point for retrieving projects.
ENDPOINT_PROJECT_RETRIEVE = "/project/api/retrieve/{project_uuid}"
#: End point for retrieving projects settings.
ENDPOINT_PROJECT_SETTING_RETRIEVE = "/project/api/settings/retrieve/{project_uuid}"


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
    return pydantic.TypeAdapter(typing.List[Project]).validate_python(result.json())


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
    return pydantic.TypeAdapter(Project).validate_python(result.json())


def project_settings_retrieve(
    server_url: str,
    api_token: str,
    project_uuid: typing.Union[str, uuid.UUID],
    app_name: typing.Optional[str],
    setting_name: typing.Optional[str],
    verify_ssl: bool = True,
) -> SettingsEntry:
    server_url = strip_trailing_slash(server_url)
    queries = []
    if app_name:
        queries.append(f"app_name={app_name}")
    if setting_name:
        queries.append(f"setting_name={setting_name}")
    query = "&".join(queries)
    if query:
        query = f"?{query}"
    endpoint = f"{server_url}{ENDPOINT_PROJECT_SETTING_RETRIEVE}{query}".format(
        project_uuid=project_uuid
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    raise_for_status(result)
    return pydantic.TypeAdapter(SettingsEntry).validate_python(result.json())
