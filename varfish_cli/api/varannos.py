"""Implementation of API operation on varannos"""


import typing
import uuid

from logzero import logger
import requests

from varfish_cli.api.models import CONVERTER, VarAnnoSetEntryV1, VarAnnoSetV1
from varfish_cli.common import strip_trailing_slash
from varfish_cli.exceptions import RestApiCallException

#: End point for listing & creating VarAnnoSets
ENDPOINT_VARANNOSET_LISTCREATE = "/varannos/api/varannoset/list-create/{project_uuid}"
#: End point for retrieving & updating & destroying VarAnnoSets.
ENDPOINT_VARANNOSET_RETRIEVEUPDATEDESTROY = (
    "/varannos/api/varannoset/retrieve-update-destroy/{varannoset_uuid}"
)
#: End point for listing & creating VarAnnoSetEntries.
ENDPOINT_VARANNOSETENTRY_LISTCREATE = "/varannos/api/varannosetentry/list-create/{varannoset_uuid}"
#: End point for retrieving & updating & destroying VarAnnoSetEntries.
ENDPOINT_VARANNOSETENTRY_RETRIEVEUPDATEDESTROY = (
    "/varannos/api/varannosetentry/retrieve-update-destroy/{varannosetentry_uuid}"
)


def raise_for_status(response):
    if not response.ok:
        raise RestApiCallException(f"Problem with API call: {response.text}.")


def varannoset_list(
    server_url: str,
    api_token: str,
    project_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> typing.List[VarAnnoSetV1]:
    """Listing of varannosets from a project UUID."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_VARANNOSET_LISTCREATE.format(project_uuid=project_uuid),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    raise_for_status(result)
    return CONVERTER.structure(result.json(), typing.List[VarAnnoSetV1])


def varannoset_create(
    server_url: str,
    api_token: str,
    project_uuid: typing.Union[str, uuid.UUID],
    payload: VarAnnoSetV1,
    verify_ssl: bool = True,
) -> VarAnnoSetV1:
    """Creating of of varannosets inside a project."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_VARANNOSET_LISTCREATE.format(project_uuid=project_uuid),
    )
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.post(
        endpoint, headers=headers, data=CONVERTER.unstructure(payload), verify=verify_ssl
    )
    raise_for_status(result)
    return CONVERTER.structure(result.json(), typing.List[VarAnnoSetV1])


def varannoset_retrieve(
    server_url: str,
    api_token: str,
    varannoset_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> VarAnnoSetV1:
    """Retrieve varannoset from its UUID."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_VARANNOSET_RETRIEVEUPDATEDESTROY.format(varannoset_uuid=varannoset_uuid),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    raise_for_status(result)
    return CONVERTER.structure(result.json(), VarAnnoSetV1)


def varannoset_update(
    server_url: str,
    api_token: str,
    varannoset_uuid: typing.Union[str, uuid.UUID],
    payload: VarAnnoSetV1,
    verify_ssl: bool = True,
) -> VarAnnoSetV1:
    """Update single varannoset at its UUID."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_VARANNOSET_RETRIEVEUPDATEDESTROY.format(varannoset_uuid=varannoset_uuid),
    )
    logger.debug("Sending PATCH request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.patch(
        endpoint, headers=headers, data=CONVERTER.unstructure(payload), verify=verify_ssl
    )
    raise_for_status(result)
    return CONVERTER.structure(result.json(), VarAnnoSetV1)


def varannoset_destroy(
    server_url: str,
    api_token: str,
    varannoset_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> None:
    """Delete varannoset at its UUID."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_VARANNOSET_RETRIEVEUPDATEDESTROY.format(varannoset_uuid=varannoset_uuid),
    )
    logger.debug("Sending DELETE request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.delete(endpoint, headers=headers, verify=verify_ssl)
    raise_for_status(result)


def varannosetentry_list(
    server_url: str,
    api_token: str,
    varannoset_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> typing.List[VarAnnoSetEntryV1]:
    """Listing of varannosetentries from a project UUID."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_VARANNOSETENTRY_LISTCREATE.format(varannoset_uuid=varannoset_uuid),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    raise_for_status(result)
    return CONVERTER.structure(result.json(), typing.List[VarAnnoSetEntryV1])


def varannosetentry_create(
    server_url: str,
    api_token: str,
    varannoset_uuid: typing.Union[str, uuid.UUID],
    payload: VarAnnoSetEntryV1,
    verify_ssl: bool = True,
) -> VarAnnoSetEntryV1:
    """Creating of of varannosetentries inside a project."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_VARANNOSETENTRY_LISTCREATE.format(varannoset_uuid=varannoset_uuid),
    )
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.post(
        endpoint, headers=headers, data=CONVERTER.unstructure(payload), verify=verify_ssl
    )
    raise_for_status(result)
    return CONVERTER.structure(result.json(), typing.List[VarAnnoSetEntryV1])


def varannosetentry_retrieve(
    server_url: str,
    api_token: str,
    varannosetentry_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> VarAnnoSetEntryV1:
    """Retrieve varannosetentry from its UUID."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_VARANNOSETENTRY_RETRIEVEUPDATEDESTROY.format(
            varannosetentry_uuid=varannosetentry_uuid
        ),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    raise_for_status(result)
    return CONVERTER.structure(result.json(), VarAnnoSetEntryV1)


def varannosetentry_update(
    server_url: str,
    api_token: str,
    varannosetentry_uuid: typing.Union[str, uuid.UUID],
    payload: VarAnnoSetEntryV1,
    verify_ssl: bool = True,
) -> VarAnnoSetEntryV1:
    """Update single varannosetentry at its UUID."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_VARANNOSETENTRY_RETRIEVEUPDATEDESTROY.format(
            varannosetentry_uuid=varannosetentry_uuid
        ),
    )
    logger.debug("Sending PATCH request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.patch(
        endpoint, headers=headers, data=CONVERTER.unstructure(payload), verify=verify_ssl
    )
    raise_for_status(result)
    return CONVERTER.structure(result.json(), VarAnnoSetEntryV1)


def varannosetentry_destroy(
    server_url: str,
    api_token: str,
    varannosetentry_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> None:
    """Delete varannosetentry at its UUID."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_VARANNOSETENTRY_RETRIEVEUPDATEDESTROY.format(
            varannosetentry_uuid=varannosetentry_uuid
        ),
    )
    logger.debug("Sending DELETE request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.delete(endpoint, headers=headers, verify=verify_ssl)
    raise_for_status(result)
