"""Implementation of API operations on cases."""

import json
from json import JSONDecodeError
import typing
import uuid

import attr
from logzero import logger
import requests
from simplejson import JSONDecodeError as SimpleJSONDecodeError

from varfish_cli.api import models
from varfish_cli.api.models import (
    CONVERTER,
    BamQcFile,
    Case,
    CaseGeneAnnotationFile,
    CaseImportInfo,
    CaseQueryResultV1,
    CaseQueryV1,
    DatabaseInfoFile,
    EffectsFile,
    GenotypeFile,
    QueryShortcutsResultV1,
    SmallVariantV1,
    VariantSetImportInfo,
)
from varfish_cli.common import strip_trailing_slash

from ..exceptions import RestApiCallException

ACCEPT_API_VARFISH = ""


#: End point for listing cases.
ENDPOINT_CASE_LIST = "/variants/api/case/list/{project_uuid}/"
#: End point for fetching case information.
ENDPOINT_CASE_RETRIEVE = "/variants/api/case/retrieve/{case_uuid}"
#: End point for listing case import infos.
ENDPOINT_CASE_IMPORT_INFO_LIST = "/importer/api/case-import-info/{project_uuid}/"
#: End point for creating case import infos.
ENDPOINT_CASE_IMPORT_INFO_CREATE = ENDPOINT_CASE_IMPORT_INFO_LIST
#: End point for updating case import infos.
ENDPOINT_CASE_IMPORT_INFO_UPDATE = (
    "/importer/api/case-import-info/{project_uuid}/{case_import_info_uuid}/"
)
#: End point for retrieving case import info.
ENDPOINT_CASE_IMPORT_INFO_RETRIEVE = ENDPOINT_CASE_IMPORT_INFO_UPDATE
#: End point for listing import variant set infos.
ENDPOINT_VARIANT_SET_IMPORT_INFO_LIST = (
    "/importer/api/variant-set-import-info/{case_import_info_uuid}/"
)
#: End point for creating import variant set infos.
ENDPOINT_VARIANT_SET_IMPORT_INFO_CREATE = ENDPOINT_VARIANT_SET_IMPORT_INFO_LIST
#: End point for creating import variant set infos.
ENDPOINT_VARIANT_SET_IMPORT_INFO_UPDATE = (
    "/importer/api/variant-set-import-info/{case_import_info_uuid}/{variant_set_import_info_uuid}/"
)
#: End point for listing BAM QC files.
ENDPOINT_BAM_QC_FILE_LIST = "/importer/api/bam-qc-file/{case_import_info_uuid}/"
#: End point for creating BAM QC files.
ENDPOINT_BAM_QC_FILE_CREATE = ENDPOINT_BAM_QC_FILE_LIST
#: End point for destroy BAM QC files
ENDPOINT_BAM_QC_FILE_DESTROY = (
    "/importer/api/bam-qc-file/{case_import_info_uuid}/{bam_qc_file_uuid}/"
)
#: End point for listing gene annotation files.
ENDPOINT_CASE_GENE_ANNOTATION_FILE_LIST = (
    "/importer/api/case-gene-annotation-file/{case_import_info_uuid}/"
)
#: End point for creating gene annotation files.
ENDPOINT_CASE_GENE_ANNOTATION_FILE_CREATE = ENDPOINT_CASE_GENE_ANNOTATION_FILE_LIST
#: End point for destroy gene annotation files
ENDPOINT_CASE_GENE_ANNOTATION_FILE_DESTROY = "/importer/api/case-gene-annotation-file/{case_import_info_uuid}/{case_gene_annotation_file_uuid}/"
#: End point for listing genotype files.
ENDPOINT_GENOTYPE_FILE_LIST = "/importer/api/genotype-file/{variant_set_import_info_uuid}/"
#: End point for creating genotype files.
ENDPOINT_GENOTYPE_FILE_CREATE = ENDPOINT_GENOTYPE_FILE_LIST
#: End point for destroying genotype files.
ENDPOINT_GENOTYPE_FILE_DESTROY = (
    "/importer/api/genotype-file/{variant_set_import_info_uuid}/{genotype_file_uuid}/"
)
#: End point for listing genotype files.
ENDPOINT_EFFECTS_FILE_LIST = "/importer/api/effects-file/{variant_set_import_info_uuid}/"
#: End point for creating genotype files.
ENDPOINT_EFFECTS_FILE_CREATE = ENDPOINT_EFFECTS_FILE_LIST
#: End point for destroying effects files.
ENDPOINT_EFFECTS_FILE_DESTROY = (
    "/importer/api/effects-file/{variant_set_import_info_uuid}/{effects_file_uuid}/"
)
#: End point for listing genotype files.
ENDPOINT_DB_INFO_FILE_LIST = "/importer/api/database-info-file/{variant_set_import_info_uuid}/"
#: End point for creating genotype files.
ENDPOINT_DB_INFO_FILE_CREATE = ENDPOINT_DB_INFO_FILE_LIST
#: End point for destroying genotype files.
ENDPOINT_DB_INFO_FILE_DESTROY = (
    "/importer/api/database-info-file/{variant_set_import_info_uuid}/{db_info_file_uuid}/"
)

#: End point for listing case queries.
ENDPOINT_CASE_QUERY_LIST = "/variants/api/query-case/list/{case_uuid}/"
#: End point for creating case queries.
ENDPOINT_CASE_QUERY_CREATE = "/variants/api/query-case/create/{case_uuid}/"
#: End point for retrieving case queries.
ENDPOINT_CASE_QUERY_RETRIEVE = "/variants/api/query-case/retrieve/{query_uuid}/"
#: End point for obtaining case query status.
ENDPOINT_CASE_QUERY_STATUS = "/variants/api/query-case/status/{query_uuid}/"
#: End point for updating case query.
ENDPOINT_CASE_QUERY_UPDATE = "/variants/api/query-case/update/{query_uuid}/"
#: End point for fetching case query results.
ENDPOINT_CASE_QUERY_FETCH_RESULTS = "/variants/api/query-case/results/{query_uuid}/"
#: End point for generating query parameters from shortcuts.
ENDPOINT_CASE_QUERY_SETTINGS_SHORTCUT = (
    "/variants/api/query-case/query-settings-shortcut/{case_uuid}/"
)


def _construct_rest_api_call_exception(response: requests.Response) -> RestApiCallException:
    try:
        msg = "REST API returned status code %d: %s" % (
            response.status_code,
            " ".join([" ".join(v) for v in response.json().values()]),
        )
    except (JSONDecodeError, SimpleJSONDecodeError):
        msg = "REST API returned status code %d: %s" % (response.status_code, response.content)
    return RestApiCallException(msg)


def case_list(
    server_url: str,
    api_token: str,
    project_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> typing.List[Case]:
    """Listing of cases from a project UUID."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (server_url, ENDPOINT_CASE_LIST.format(project_uuid=project_uuid))
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    result.raise_for_status()
    return CONVERTER.structure(result.json(), typing.List[Case])


def case_retrieve(
    server_url: str,
    api_token: str,
    case_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> CaseImportInfo:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (server_url, ENDPOINT_CASE_RETRIEVE.format(case_uuid=case_uuid))
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    result.raise_for_status()
    return CONVERTER.structure(result.json(), CaseImportInfo)


def case_import_info_list(
    server_url: str,
    api_token: str,
    project_uuid: typing.Union[str, uuid.UUID],
    owner=None,
    verify_ssl: bool = True,
) -> typing.List[CaseImportInfo]:
    """Listing case import infos from a project UUID."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_CASE_IMPORT_INFO_LIST.format(project_uuid=project_uuid),
    )
    headers = {"Authorization": "Token %s" % api_token}
    if owner:
        params = {"owner": owner}
    else:
        params = None
    logger.debug("Sending GET request to end point %s, params: %s", endpoint, params)
    result = requests.get(endpoint, headers=headers, params=params, verify=verify_ssl)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), typing.List[CaseImportInfo])


def case_import_info_retrieve(
    server_url: str,
    api_token: str,
    project_uuid: typing.Union[str, uuid.UUID],
    info_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> CaseImportInfo:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_CASE_IMPORT_INFO_RETRIEVE.format(
            project_uuid=project_uuid, case_import_info_uuid=info_uuid
        ),
    )
    headers = {"Authorization": "Token %s" % api_token}
    logger.debug("Sending GET request to end point %s", endpoint)
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), CaseImportInfo)


def case_import_info_create(
    server_url: str,
    api_token: str,
    project_uuid: typing.Union[str, uuid.UUID],
    data: models.CaseImportInfo,
    verify_ssl: bool = True,
) -> CaseImportInfo:
    """Create new CaseImportInfo on server."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_CASE_IMPORT_INFO_CREATE.format(project_uuid=project_uuid),
    )
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    logger.debug("json=%s", CONVERTER.unstructure(data))
    result = requests.post(
        endpoint, headers=headers, json=CONVERTER.unstructure(data), verify=verify_ssl
    )
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), CaseImportInfo)


def case_import_info_update(
    server_url: str,
    api_token: str,
    project_uuid: typing.Union[str, uuid.UUID],
    case_import_info_uuid: typing.Union[str, uuid.UUID],
    data: models.CaseImportInfo,
    verify_ssl: bool = True,
) -> CaseImportInfo:
    """Update CaseImportInfo on server."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_CASE_IMPORT_INFO_UPDATE.format(
            project_uuid=project_uuid, case_import_info_uuid=case_import_info_uuid
        ),
    )
    logger.debug("Sending PUT request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    logger.debug("json=%s", CONVERTER.unstructure(data))
    result = requests.put(
        endpoint, headers=headers, json=CONVERTER.unstructure(data), verify=verify_ssl
    )
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), CaseImportInfo)


def variant_set_import_info_list(
    server_url: str,
    api_token: str,
    case_import_info_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> typing.List[VariantSetImportInfo]:
    """List variant set import infos."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_VARIANT_SET_IMPORT_INFO_LIST.format(case_import_info_uuid=case_import_info_uuid),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), typing.List[VariantSetImportInfo])


def variant_set_import_info_create(
    server_url: str,
    api_token: str,
    case_import_info_uuid: typing.Union[str, uuid.UUID],
    data: VariantSetImportInfo,
    verify_ssl: bool = True,
) -> typing.List[VariantSetImportInfo]:
    """Create variant set import info."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_VARIANT_SET_IMPORT_INFO_CREATE.format(case_import_info_uuid=case_import_info_uuid),
    )
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.post(
        endpoint, headers=headers, json=CONVERTER.unstructure(data), verify=verify_ssl
    )
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), VariantSetImportInfo)


def variant_set_import_info_update(
    server_url: str,
    api_token: str,
    case_import_info_uuid: typing.Union[str, uuid.UUID],
    variant_set_import_info_uuid: typing.Union[str, uuid.UUID],
    data: VariantSetImportInfo,
    verify_ssl: bool = True,
) -> VariantSetImportInfo:
    """Create variant set import info."""
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_VARIANT_SET_IMPORT_INFO_UPDATE.format(
            case_import_info_uuid=case_import_info_uuid,
            variant_set_import_info_uuid=variant_set_import_info_uuid,
        ),
    )
    logger.debug("Sending PUT request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    logger.debug("json=%s", CONVERTER.unstructure(data))
    result = requests.put(
        endpoint, headers=headers, json=CONVERTER.unstructure(data), verify=verify_ssl
    )
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), VariantSetImportInfo)


def bam_qc_file_list(
    server_url: str,
    api_token: str,
    case_import_info_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> typing.List[BamQcFile]:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_BAM_QC_FILE_LIST.format(case_import_info_uuid=case_import_info_uuid),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), typing.List[BamQcFile])


def bam_qc_file_upload(
    server_url: str,
    api_token: str,
    case_import_info_uuid: typing.Union[str, uuid.UUID],
    data: BamQcFile,
    files: typing.Dict[str, typing.BinaryIO],
    verify_ssl: bool = True,
) -> BamQcFile:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_BAM_QC_FILE_CREATE.format(case_import_info_uuid=case_import_info_uuid),
    )
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.post(
        endpoint, headers=headers, data=CONVERTER.unstructure(data), files=files, verify=verify_ssl
    )
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), BamQcFile)


def bam_qc_file_destroy(
    server_url: str,
    api_token: str,
    case_import_info_uuid: typing.Union[str, uuid.UUID],
    bam_qc_file_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
):
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_BAM_QC_FILE_DESTROY.format(
            case_import_info_uuid=case_import_info_uuid, bam_qc_file_uuid=bam_qc_file_uuid
        ),
    )
    logger.debug("Sending DELETE request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.delete(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)


def case_gene_annotation_file_list(
    server_url: str,
    api_token: str,
    case_import_info_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> typing.List[CaseGeneAnnotationFile]:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_CASE_GENE_ANNOTATION_FILE_LIST.format(case_import_info_uuid=case_import_info_uuid),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), typing.List[CaseGeneAnnotationFile])


def case_gene_annotation_file_upload(
    server_url: str,
    api_token: str,
    case_import_info_uuid: typing.Union[str, uuid.UUID],
    data: CaseGeneAnnotationFile,
    files: typing.Dict[str, typing.BinaryIO],
    verify_ssl: bool = True,
) -> CaseGeneAnnotationFile:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_CASE_GENE_ANNOTATION_FILE_CREATE.format(
            case_import_info_uuid=case_import_info_uuid
        ),
    )
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.post(
        endpoint, headers=headers, data=CONVERTER.unstructure(data), files=files, verify=verify_ssl
    )
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), CaseGeneAnnotationFile)


def case_gene_annotation_file_destroy(
    server_url: str,
    api_token: str,
    case_import_info_uuid: typing.Union[str, uuid.UUID],
    case_gene_annotation_file_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
):
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_CASE_GENE_ANNOTATION_FILE_DESTROY.format(
            case_import_info_uuid=case_import_info_uuid,
            case_gene_annotation_file_uuid=case_gene_annotation_file_uuid,
        ),
    )
    logger.debug("Sending DELETE request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.delete(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)


def genotype_file_list(
    server_url: str,
    api_token: str,
    variant_set_import_info_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> typing.List[GenotypeFile]:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_GENOTYPE_FILE_LIST.format(
            variant_set_import_info_uuid=variant_set_import_info_uuid
        ),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), typing.List[GenotypeFile])


def genotype_file_upload(
    server_url: str,
    api_token: str,
    variant_set_import_info_uuid: typing.Union[str, uuid.UUID],
    data: GenotypeFile,
    files: typing.Dict[str, typing.BinaryIO],
    verify_ssl: bool = True,
) -> GenotypeFile:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_GENOTYPE_FILE_CREATE.format(
            variant_set_import_info_uuid=variant_set_import_info_uuid
        ),
    )
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.post(
        endpoint, headers=headers, data=CONVERTER.unstructure(data), files=files, verify=verify_ssl
    )
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), GenotypeFile)


def genotype_file_destroy(
    server_url: str,
    api_token: str,
    variant_set_import_info_uuid: typing.Union[str, uuid.UUID],
    genotype_file_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
):
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_GENOTYPE_FILE_DESTROY.format(
            variant_set_import_info_uuid=variant_set_import_info_uuid,
            genotype_file_uuid=genotype_file_uuid,
        ),
    )
    logger.debug("Sending DELETE request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.delete(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)


def effects_file_list(
    server_url: str,
    api_token: str,
    variant_set_import_info_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> typing.List[EffectsFile]:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_EFFECTS_FILE_LIST.format(
            variant_set_import_info_uuid=variant_set_import_info_uuid
        ),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), typing.List[EffectsFile])


def effects_file_upload(
    server_url: str,
    api_token: str,
    variant_set_import_info_uuid: typing.Union[str, uuid.UUID],
    data: EffectsFile,
    files: typing.Dict[str, typing.BinaryIO],
    verify_ssl: bool = True,
) -> EffectsFile:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_EFFECTS_FILE_CREATE.format(
            variant_set_import_info_uuid=variant_set_import_info_uuid
        ),
    )
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.post(
        endpoint, headers=headers, data=CONVERTER.unstructure(data), files=files, verify=verify_ssl
    )
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), EffectsFile)


def effects_file_destroy(
    server_url: str,
    api_token: str,
    variant_set_import_info_uuid: typing.Union[str, uuid.UUID],
    effects_file_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
):
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_EFFECTS_FILE_DESTROY.format(
            variant_set_import_info_uuid=variant_set_import_info_uuid,
            effects_file_uuid=effects_file_uuid,
        ),
    )
    logger.debug("Sending DELETE request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.delete(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)


def db_info_file_list(
    server_url: str,
    api_token: str,
    variant_set_import_info_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
) -> typing.List[DatabaseInfoFile]:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_DB_INFO_FILE_LIST.format(
            variant_set_import_info_uuid=variant_set_import_info_uuid
        ),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), typing.List[DatabaseInfoFile])


def db_info_file_upload(
    server_url: str,
    api_token: str,
    variant_set_import_info_uuid: typing.Union[str, uuid.UUID],
    data: DatabaseInfoFile,
    files: typing.Dict[str, typing.BinaryIO],
    verify_ssl: bool = True,
) -> DatabaseInfoFile:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_DB_INFO_FILE_CREATE.format(
            variant_set_import_info_uuid=variant_set_import_info_uuid
        ),
    )
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.post(
        endpoint, headers=headers, data=CONVERTER.unstructure(data), files=files, verify=verify_ssl
    )
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except (JSONDecodeError, SimpleJSONDecodeError):
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)
    else:
        return CONVERTER.structure(result.json(), DatabaseInfoFile)


def db_info_file_destroy(
    server_url: str,
    api_token: str,
    variant_set_import_info_uuid: typing.Union[str, uuid.UUID],
    db_info_file_uuid: typing.Union[str, uuid.UUID],
    verify_ssl: bool = True,
):
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_DB_INFO_FILE_DESTROY.format(
            variant_set_import_info_uuid=variant_set_import_info_uuid,
            db_info_file_uuid=db_info_file_uuid,
        ),
    )
    logger.debug("Sending DELETE request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.delete(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        try:
            msg = "REST API returned status code %d: %s" % (
                result.status_code,
                " ".join([" ".join(v) for v in result.json().values()]),
            )
        except JSONDecodeError:
            msg = "REST API returned status code %d: %s" % (result.status_code, result.content)
        raise RestApiCallException(msg)


def small_var_query_list(
    server_url: str, api_token: str, case_uuid: uuid.UUID, verify_ssl: bool = True
) -> typing.Dict[str, typing.Any]:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (server_url, ENDPOINT_CASE_QUERY_LIST.format(case_uuid=case_uuid))
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        raise _construct_rest_api_call_exception(result)
    return CONVERTER.structure(result.json(), typing.List[CaseQueryResultV1])


def small_var_query_create(
    server_url: str,
    api_token: str,
    case_uuid: uuid.UUID,
    case_query: models.CaseQueryV1,
    verify_ssl: bool = True,
) -> typing.Dict[str, typing.Any]:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (server_url, ENDPOINT_CASE_QUERY_CREATE.format(case_uuid=case_uuid))
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    logger.debug("data = %s", json.dumps(CONVERTER.unstructure(case_query), indent="  "))
    result = requests.post(
        endpoint, json=CONVERTER.unstructure(case_query), headers=headers, verify=verify_ssl
    )
    if not result.ok:
        raise _construct_rest_api_call_exception(result)
    return CONVERTER.structure(result.json(), CaseQueryV1)


def small_var_query_retrieve(
    server_url: str, api_token: str, query_uuid: uuid.UUID, verify_ssl: bool = True
) -> typing.Dict[str, typing.Any]:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (server_url, ENDPOINT_CASE_QUERY_RETRIEVE.format(query_uuid=query_uuid))
    logger.debug("Sending POST request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        raise _construct_rest_api_call_exception(result)
    return result.json()


def small_var_query_status(
    server_url: str, api_token: str, query_uuid: uuid.UUID, verify_ssl: bool = True
) -> typing.Dict[str, typing.Any]:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (server_url, ENDPOINT_CASE_QUERY_STATUS.format(query_uuid=query_uuid))
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        raise _construct_rest_api_call_exception(result)
    return result.json()


def small_var_query_update(
    server_url: str,
    api_token: str,
    query_uuid: uuid.UUID,
    case_query: models.CaseQueryV1,
    verify_ssl: bool = True,
) -> typing.Dict[str, typing.Any]:
    headers = {"Authorization": "Token %s" % api_token}

    server_url = strip_trailing_slash(server_url)
    endpoint_get = "%s%s" % (server_url, ENDPOINT_CASE_QUERY_RETRIEVE.format(query_uuid=query_uuid))
    logger.debug("Sending GET request to end point %s", endpoint_get)
    result_get = requests.get(endpoint_get, headers=headers, verify=verify_ssl)
    if not result_get.ok:
        raise _construct_rest_api_call_exception(result_get)

    endpoint_put = "%s%s" % (server_url, ENDPOINT_CASE_QUERY_UPDATE.format(query_uuid=query_uuid))
    logger.debug("Sending PUT request to end point %s", endpoint_put)
    if case_query.public is None:
        case_query = attr.evolve(case_query, public=result_get.json()["public"])
    if not case_query.name:
        case_query = attr.evolve(case_query, name="")
    result_put = requests.put(
        endpoint_put, data=CONVERTER.unstructure(case_query), headers=headers, verify=verify_ssl
    )
    if not result_put.ok:
        raise _construct_rest_api_call_exception(result_put)
    return result_put.json()


def small_var_query_fetch_results(
    server_url: str, api_token: str, query_uuid: uuid.UUID, verify_ssl: bool = True
) -> typing.Dict[str, typing.Any]:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_CASE_QUERY_FETCH_RESULTS.format(query_uuid=query_uuid),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    result = requests.get(endpoint, headers=headers, verify=verify_ssl)
    if not result.ok:
        raise _construct_rest_api_call_exception(result)
    return CONVERTER.structure(result.json(), typing.List[SmallVariantV1])


def small_var_query_settings_shortcut(
    server_url: str,
    api_token: str,
    case_uuid: uuid.UUID,
    database: str,
    quick_preset: str,
    inheritance: typing.Optional[str] = None,
    frequency: typing.Optional[str] = None,
    impact: typing.Optional[str] = None,
    quality: typing.Optional[str] = None,
    chromosomes: typing.Optional[str] = None,
    flags_etc: typing.Optional[str] = None,
    verify_ssl: bool = True,
) -> typing.Dict[str, typing.Any]:
    server_url = strip_trailing_slash(server_url)
    endpoint = "%s%s" % (
        server_url,
        ENDPOINT_CASE_QUERY_SETTINGS_SHORTCUT.format(case_uuid=case_uuid),
    )
    logger.debug("Sending GET request to end point %s", endpoint)
    headers = {"Authorization": "Token %s" % api_token}
    params = {"database": database, "quick_preset": quick_preset}
    params.pop("database")  # TODO: REMOVE ME
    if inheritance:
        params["inheritance"] = inheritance
    if frequency:
        params["frequency"] = frequency
    if impact:
        params["impact"] = impact
    if quality:
        params["quality"] = quality
    if chromosomes:
        params["chromosomes"] = chromosomes
    if flags_etc:
        params["flags_etc"] = flags_etc
    result = requests.get(endpoint, headers=headers, params=params, verify=verify_ssl)
    if not result.ok:
        raise _construct_rest_api_call_exception(result)
    return CONVERTER.structure(result.json(), QueryShortcutsResultV1)
