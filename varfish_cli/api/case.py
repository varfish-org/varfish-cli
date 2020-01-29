"""Implementation of API operations on cases."""

import typing
import uuid
from json import JSONDecodeError

import requests
from logzero import logger

from . import models
from .models import (
    Case,
    CaseImportInfo,
    CONVERTER,
    VariantSetImportInfo,
    BamQcFile,
    GenotypeFile,
    EffectsFile,
    DatabaseInfoFile,
)

from ..exceptions import RestApiCallException

#: End point for listing cases.
ENDPOINT_CASE_LIST = "/variants/api/case/{project_uuid}/"
#: End point for listing case import infos.
ENDPOINT_CASE_IMPORT_INFO_LIST = "/importer/api/case-import-info/{project_uuid}/"
#: End point for creating case import infos.
ENDPOINT_CASE_IMPORT_INFO_CREATE = ENDPOINT_CASE_IMPORT_INFO_LIST
#: End point for updating case import infos.
ENDPOINT_CASE_IMPORT_INFO_UPDATE = (
    "/importer/api/case-import-info/{project_uuid}/{case_import_info_uuid}/"
)
#: End point for listing import variant set infos.
ENDPOINT_VARIANT_SET_IMPORT_INFO_LIST = (
    "/importer/api/variant-set-import-info/{case_import_info_uuid}/"
)
#: End point for creating import variant set infos.
ENDPOINT_VARIANT_SET_IMPORT_INFO_CREATE = ENDPOINT_VARIANT_SET_IMPORT_INFO_LIST
#: End point for listing BAM QC files.
ENDPOINT_BAM_QC_FILE_LIST = "/importer/api/bam-qc-file/{case_import_info_uuid}/"
#: End point for creating BAM QC files.
ENDPOINT_BAM_QC_FILE_CREATE = ENDPOINT_BAM_QC_FILE_LIST
#: End point for listing genotype files.
ENDPOINT_GENOTYPE_FILE_LIST = "/importer/api/genotype-file/{variant_set_import_info_uuid}/"
#: End point for creating genotype files.
ENDPOINT_GENOTYPE_FILE_CREATE = ENDPOINT_GENOTYPE_FILE_LIST
#: End point for listing genotype files.
ENDPOINT_EFFECTS_FILE_LIST = "/importer/api/effects-file/{variant_set_import_info_uuid}/"
#: End point for creating genotype files.
ENDPOINT_EFFECTS_FILE_CREATE = ENDPOINT_EFFECTS_FILE_LIST
#: End point for listing genotype files.
ENDPOINT_DB_INFO_FILE_LIST = "/importer/api/database-info-file/{variant_set_import_info_uuid}/"
#: End point for creating genotype files.
ENDPOINT_DB_INFO_FILE_CREATE = ENDPOINT_DB_INFO_FILE_LIST


def case_list(
    server_url: str, api_key: str, project_uuid: typing.Union[str, uuid.UUID]
) -> typing.List[Case]:
    """Listing of cases from a project UUID."""
    while server_url.endswith("/"):
        server_url = server_url[:-1]
    endpoint = "%s%s" % (server_url, ENDPOINT_CASE_LIST.format(project_uuid=project_uuid))
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_key}
    result = requests.get(endpoint, headers=headers)
    result.raise_for_status()
    return CONVERTER.structure(result.json(), typing.List[Case])


def case_import_info_list(
    server_url: str, api_key: str, project_uuid: typing.Union[str, uuid.UUID], owner=None
) -> typing.List[CaseImportInfo]:
    """Listing case import infos from a project UUID."""
    while server_url.endswith("/"):
        server_url = server_url[:-1]
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_CASE_IMPORT_INFO_LIST.format(project_uuid=project_uuid),
    )
    headers = {"Authorization": "Token %s" % api_key}
    if owner:
        params = {"owner": owner}
    else:
        params = None
    logger.debug("Sending GET request to end point %s, params: %s", endpoint, params)
    result = requests.get(endpoint, headers=headers, params=params)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except JSONDecodeError:
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), typing.List[CaseImportInfo])


def case_import_info_create(
    server_url: str,
    api_key: str,
    project_uuid: typing.Union[str, uuid.UUID],
    data: models.CaseImportInfo,
) -> CaseImportInfo:
    """Create new CaseImportInfo on server."""
    while server_url.endswith("/"):
        server_url = server_url[:-1]
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_CASE_IMPORT_INFO_CREATE.format(project_uuid=project_uuid),
    )
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_key}
    logger.debug("json=%s", CONVERTER.unstructure(data))
    result = requests.post(endpoint, headers=headers, json=CONVERTER.unstructure(data))
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except JSONDecodeError:
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), CaseImportInfo)


def case_import_info_update(
    server_url: str,
    api_key: str,
    project_uuid: typing.Union[str, uuid.UUID],
    case_import_info_uuid: typing.Union[str, uuid.UUID],
    data: models.CaseImportInfo,
) -> CaseImportInfo:
    """Update CaseImportInfo on server."""
    while server_url.endswith("/"):
        server_url = server_url[:-1]
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_CASE_IMPORT_INFO_UPDATE.format(
            project_uuid=project_uuid, case_import_info_uuid=case_import_info_uuid
        ),
    )
    logger.debug("Sending PUT request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_key}
    logger.debug("json=%s", CONVERTER.unstructure(data))
    result = requests.put(endpoint, headers=headers, json=CONVERTER.unstructure(data))
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except JSONDecodeError:
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), CaseImportInfo)


def variant_set_import_info_list(
    server_url: str, api_key: str, case_import_info_uuid: typing.Union[str, uuid.UUID]
) -> typing.List[VariantSetImportInfo]:
    """List variant set import infos."""
    while server_url.endswith("/"):
        server_url = server_url[:-1]
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_VARIANT_SET_IMPORT_INFO_LIST.format(case_import_info_uuid=case_import_info_uuid),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_key}
    result = requests.get(endpoint, headers=headers)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except JSONDecodeError:
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), typing.List[VariantSetImportInfo])


def variant_set_import_info_create(
    server_url: str,
    api_key: str,
    case_import_info_uuid: typing.Union[str, uuid.UUID],
    data: VariantSetImportInfo,
) -> typing.List[VariantSetImportInfo]:
    """Create variant set import info."""
    while server_url.endswith("/"):
        server_url = server_url[:-1]
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_VARIANT_SET_IMPORT_INFO_CREATE.format(case_import_info_uuid=case_import_info_uuid),
    )
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_key}
    result = requests.post(endpoint, headers=headers, json=CONVERTER.unstructure(data))
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except JSONDecodeError:
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), VariantSetImportInfo)


def bam_qc_file_list(
    server_url: str, api_key: str, case_import_info_uuid: typing.Union[str, uuid.UUID]
) -> typing.List[BamQcFile]:
    while server_url.endswith("/"):
        server_url = server_url[:-1]
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_BAM_QC_FILE_LIST.format(case_import_info_uuid=case_import_info_uuid),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_key}
    result = requests.get(endpoint, headers=headers)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except JSONDecodeError:
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), typing.List[BamQcFile])


def bam_qc_file_upload(
    server_url: str,
    api_key: str,
    case_import_info_uuid: typing.Union[str, uuid.UUID],
    data: BamQcFile,
    files: typing.Dict[str, typing.BinaryIO],
) -> BamQcFile:
    while server_url.endswith("/"):
        server_url = server_url[:-1]
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_BAM_QC_FILE_CREATE.format(case_import_info_uuid=case_import_info_uuid),
    )
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_key}
    result = requests.post(endpoint, headers=headers, data=CONVERTER.unstructure(data), files=files)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except JSONDecodeError:
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), BamQcFile)


def genotype_file_list(
    server_url: str, api_key: str, variant_set_import_info_uuid: typing.Union[str, uuid.UUID]
) -> typing.List[GenotypeFile]:
    while server_url.endswith("/"):
        server_url = server_url[:-1]
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_GENOTYPE_FILE_LIST.format(
            variant_set_import_info_uuid=variant_set_import_info_uuid
        ),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_key}
    result = requests.get(endpoint, headers=headers)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except JSONDecodeError:
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), typing.List[GenotypeFile])


def genotype_file_upload(
    server_url: str,
    api_key: str,
    variant_set_import_info_uuid: typing.Union[str, uuid.UUID],
    data: GenotypeFile,
    files: typing.Dict[str, typing.BinaryIO],
) -> GenotypeFile:
    while server_url.endswith("/"):
        server_url = server_url[:-1]
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_GENOTYPE_FILE_CREATE.format(
            variant_set_import_info_uuid=variant_set_import_info_uuid
        ),
    )
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_key}
    result = requests.post(endpoint, headers=headers, data=CONVERTER.unstructure(data), files=files)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except JSONDecodeError:
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), GenotypeFile)


def effects_file_list(
    server_url: str, api_key: str, variant_set_import_info_uuid: typing.Union[str, uuid.UUID]
) -> typing.List[EffectsFile]:
    while server_url.endswith("/"):
        server_url = server_url[:-1]
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_EFFECTS_FILE_LIST.format(
            variant_set_import_info_uuid=variant_set_import_info_uuid
        ),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_key}
    result = requests.get(endpoint, headers=headers)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except JSONDecodeError:
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), typing.List[EffectsFile])


def effects_file_upload(
    server_url: str,
    api_key: str,
    variant_set_import_info_uuid: typing.Union[str, uuid.UUID],
    data: EffectsFile,
    files: typing.Dict[str, typing.BinaryIO],
) -> EffectsFile:
    while server_url.endswith("/"):
        server_url = server_url[:-1]
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_EFFECTS_FILE_CREATE.format(
            variant_set_import_info_uuid=variant_set_import_info_uuid
        ),
    )
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_key}
    result = requests.post(endpoint, headers=headers, data=CONVERTER.unstructure(data), files=files)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except JSONDecodeError:
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), EffectsFile)


def db_info_file_list(
    server_url: str, api_key: str, variant_set_import_info_uuid: typing.Union[str, uuid.UUID]
) -> typing.List[DatabaseInfoFile]:
    while server_url.endswith("/"):
        server_url = server_url[:-1]
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_DB_INFO_FILE_LIST.format(
            variant_set_import_info_uuid=variant_set_import_info_uuid
        ),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_key}
    result = requests.get(endpoint, headers=headers)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except JSONDecodeError:
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), typing.List[DatabaseInfoFile])


def db_info_file_upload(
    server_url: str,
    api_key: str,
    variant_set_import_info_uuid: typing.Union[str, uuid.UUID],
    data: DatabaseInfoFile,
    files: typing.Dict[str, typing.BinaryIO],
) -> DatabaseInfoFile:
    while server_url.endswith("/"):
        server_url = server_url[:-1]
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_DB_INFO_FILE_CREATE.format(
            variant_set_import_info_uuid=variant_set_import_info_uuid
        ),
    )
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_key}
    result = requests.post(endpoint, headers=headers, data=CONVERTER.unstructure(data), files=files)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except JSONDecodeError:
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), DatabaseInfoFile)
