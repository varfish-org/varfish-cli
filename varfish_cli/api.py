"""Code for accessing VarFish Server API."""
import datetime
import uuid

import attr
import cattr
import typing

import dateutil.parser
from logzero import logger
import requests


def setup_converter() -> cattr.Converter:
    result = cattr.Converter()
    result.register_structure_hook(uuid.UUID, lambda d, _: uuid.UUID(d))
    result.register_structure_hook(datetime.datetime, lambda d, _: dateutil.parser.parse(d))
    return result


#: cattr Converter to use
CONVERTER = setup_converter()


@attr.s(frozen=True, auto_attribs=True)
class PedigreeMember:
    """Represent a pedigree member as returned by VarFish's API."""

    #: The name of the member.
    name: str

    #: The father name of the member.
    father: str

    #: The mother name of the member.
    mother: str

    #: The sex of the member.
    sex: str

    #: The disease state of the member.
    affected: str

    #: Whether or not the member has genotype values in the call set.
    has_gt_entries: bool


@attr.s(frozen=True, auto_attribs=True)
class Case:
    """Represent a case as returned by VarFish's API."""

    #: The case identifier.
    sodar_uuid: uuid.UUID

    #: Date of creation.
    date_created: datetime.datetime

    #: Date of last modification.
    date_modified: datetime.datetime

    #: Name of the case.
    name: str

    #: Name of the index individual.
    index: str

    #: List of pedigree members.
    pedigree: typing.List[PedigreeMember]

    #: Number of small variants in case.
    num_small_vars: typing.Optional[int]

    #: Number of SVs in case.
    num_svs: typing.Optional[int]


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
