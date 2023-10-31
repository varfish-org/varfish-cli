"""Data models for supporting the VarFish CLI."""

import datetime
from enum import Enum, unique
import typing
import uuid

import attr
import cattr
import dateutil.parser


@unique
class ProjectType(Enum):
    """Enumeration of possible project types."""

    #: Container for other categories or projects but not primary data.
    CATEGORY = "CATEGORY"
    #: Project containing primary data but no other projects.
    PROJECT = "PROJECT"


@attr.s(frozen=True, auto_attribs=True)
class Project:
    #: The project identifier.
    sodar_uuid: uuid.UUID
    #: Parent category UUID, if any.
    parent: typing.Optional[uuid.UUID]
    #: Project title.
    title: str
    #: Project type.
    type: ProjectType
    #: Project description.
    description: str
    #: Markdown README string.
    readme: str
    #: Whether public guest access is allowed.
    public_guest_access: bool
    #: Whether the project has been archived.
    archive: bool


@attr.s(frozen=True, auto_attribs=True)
class PedigreeMember:
    """Represent a pedigree member as returned by the VarFish API."""

    #: The name of the member.
    name: str
    #: The father name of the member.
    father: str
    #: The mother name of the member.
    mother: str
    #: The sex of the member.
    sex: int
    #: The disease state of the member.
    affected: int
    #: Whether or not the member has genotype values in the call set.
    has_gt_entries: bool


@attr.s(frozen=True, auto_attribs=True)
class Case:
    """Represent a case as returned by the VarFish API."""

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
    num_small_vars: typing.Optional[int] = None
    #: Number of SVs in case.
    num_svs: typing.Optional[int] = None
    #: Cusom User Notes
    notes: typing.Optional[str] = None
    #: Status of case. Can be either "active" "closed-<solved|unsolved>" or "initial"
    status: typing.Optional[str] = None

    @property
    def members(self):
        return [m.name for m in self.pedigree]


class CaseImportState(Enum):
    """Enumeration for the states."""

    #: Draft state, allows modification.
    DRAFT = "draft"
    #: Submitted for import.
    SUBMITTED = "submitted"
    #: Imported into database.
    IMPORTED = "imported"
    #: Previously in database but not any more.
    EVICTED = "evicted"
    #: Failed import.
    FAILED = "failed"


class VariantSetImportState(Enum):
    """Enumeration for the states."""

    #: Draft state, allows modification.
    DRAFT = "draft"
    #: Files uploaded for import.
    UPLOADED = "uploaded"
    #: Imported into database.
    IMPORTED = "imported"
    #: Previously in database but not any more.
    EVICTED = "evicted"
    #: Failed import.
    FAILED = "failed"


class GenomeBuild(Enum):
    """Enumeration of possible genome builds."""

    #: GRCh37.
    GRCH37 = "GRCh37"
    #: GRCh38
    GRCH38 = "GRCh38"


@attr.s(frozen=True, auto_attribs=True)
class CaseImportInfo:
    """Case import information as returned by the VarFish API."""

    #: Genome build
    release: GenomeBuild
    #: Case name.
    name: str
    #: Index name.
    index: str
    #: Pedigree information.
    pedigree: typing.List[PedigreeMember]
    #: The case identifier.
    sodar_uuid: typing.Optional[uuid.UUID] = None
    #: Owner.
    owner: typing.Optional[str] = None
    #: Date of creation.
    date_created: typing.Optional[datetime.datetime] = None
    #: Date of last modification.
    date_modified: typing.Optional[datetime.datetime] = None
    #: UUID of the remote project
    project: typing.Optional[uuid.UUID] = None
    #: UUID of the remote case.
    case: typing.Optional[uuid.UUID] = None
    #: State.
    state: CaseImportState = CaseImportState.DRAFT
    #: Notes
    notes: typing.Optional[str] = None
    #: Tags
    tags: typing.List[str] = attr.Factory(list)


class CaseVariantType(Enum):
    """Enumeration of variant types in a case."""

    #: Small variants.
    SMALL = "SMALL"
    #: Structural variants.
    STRUCTURAL = "STRUCTURAL"


@attr.s(frozen=True, auto_attribs=True)
class VariantSetImportInfo:
    """Information on importing a set of variants."""

    #: The genome build.
    genomebuild: GenomeBuild
    #: The variant type.
    variant_type: CaseVariantType

    #: The case identifier.
    sodar_uuid: typing.Optional[uuid.UUID] = None
    #: Date of creation.
    date_created: typing.Optional[datetime.datetime] = None
    #: Date of last modification.
    date_modified: typing.Optional[datetime.datetime] = None
    #: UUID of the linked ``CaseImportInfo``.
    case_import_info: typing.Optional[uuid.UUID] = None
    #: State.
    state: VariantSetImportState = VariantSetImportState.DRAFT


@attr.s(frozen=True, auto_attribs=True)
class BamQcFile:
    """Information for BAM QC file without the payload."""

    #: Name of the file.
    name: str
    #: MD5 sum of the file.
    md5: str

    #: The case identifier.
    sodar_uuid: typing.Optional[uuid.UUID] = None
    #: Date of creation.
    date_created: typing.Optional[datetime.datetime] = None
    #: Date of last modification.
    date_modified: typing.Optional[datetime.datetime] = None
    #: UUID of the linked ``CaseImportInfo``.
    case_import_info: typing.Optional[uuid.UUID] = None


@attr.s(frozen=True, auto_attribs=True)
class CaseGeneAnnotationFile:
    """Information for Gene Annotation file without the payload."""

    #: Name of the file.
    name: str
    #: MD5 sum of the file.
    md5: str

    #: The case identifier.
    sodar_uuid: typing.Optional[uuid.UUID] = None
    #: Date of creation.
    date_created: typing.Optional[datetime.datetime] = None
    #: Date of last modification.
    date_modified: typing.Optional[datetime.datetime] = None
    #: UUID of the linked ``CaseImportInfo``.
    case_import_info: typing.Optional[uuid.UUID] = None


@attr.s(frozen=True, auto_attribs=True)
class GenotypeFile:
    """Genotype file."""

    #: Name of the file.
    name: str
    #: MD5 sum of the file.
    md5: str

    #: The case identifier.
    sodar_uuid: typing.Optional[uuid.UUID] = None
    #: Date of creation.
    date_created: typing.Optional[datetime.datetime] = None
    #: Date of last modification.
    date_modified: typing.Optional[datetime.datetime] = None
    #: UUID of the linked ``CaseImportInfo``.
    case_import_info: typing.Optional[uuid.UUID] = None


@attr.s(frozen=True, auto_attribs=True)
class EffectsFile:
    """Effects file."""

    #: Name of the file.
    name: str
    #: MD5 sum of the file.
    md5: str

    #: The case identifier.
    sodar_uuid: typing.Optional[uuid.UUID] = None
    #: Date of creation.
    date_created: typing.Optional[datetime.datetime] = None
    #: Date of last modification.
    date_modified: typing.Optional[datetime.datetime] = None
    #: UUID of the linked ``CaseImportInfo``.
    case_import_info: typing.Optional[uuid.UUID] = None


@attr.s(frozen=True, auto_attribs=True)
class DatabaseInfoFile:
    """Database information file."""

    #: Name of the file.
    name: str
    #: MD5 sum of the file.
    md5: str

    #: The case identifier.
    sodar_uuid: typing.Optional[uuid.UUID] = None
    #: Date of creation.
    date_created: typing.Optional[datetime.datetime] = None
    #: Date of last modification.
    date_modified: typing.Optional[datetime.datetime] = None
    #: UUID of the linked ``CaseImportInfo``.
    case_import_info: typing.Optional[uuid.UUID] = None


def _setup_converter() -> cattr.Converter:
    result = cattr.Converter()
    result.register_structure_hook(uuid.UUID, lambda d, _: uuid.UUID(d))
    result.register_unstructure_hook(uuid.UUID, str)
    result.register_structure_hook(datetime.datetime, lambda d, _: dateutil.parser.parse(d))
    result.register_unstructure_hook(
        datetime.datetime,
        lambda obj: obj.replace(tzinfo=datetime.timezone.utc)
        .astimezone()
        .replace(microsecond=0)
        .isoformat(),
    )
    return result


#: cattr Converter to use
CONVERTER = _setup_converter()


@attr.s(frozen=True, auto_attribs=True)
class VarAnnoSetV1:
    """VarAnnoSet as returned by query result"""

    #: The case identifier.
    sodar_uuid: uuid.UUID
    #: Date of creation.
    date_created: datetime.datetime
    #: Date of last modification.
    date_modified: datetime.datetime

    #: Project UUID.
    project: uuid.UUID
    #: Title of the set.
    title: str
    #: Description of the set.
    description: str
    #: Genome build of the release.
    release: str
    #: Fields for the variant annotation set.
    fields: typing.List[str]


@attr.s(frozen=True, auto_attribs=True)
class VarAnnoSetEntryV1:
    """VarAnnoSet as returned by query result"""

    #: The case identifier.
    sodar_uuid: uuid.UUID
    #: Date of creation.
    date_created: datetime.datetime
    #: Date of last modification.
    date_modified: datetime.datetime

    #: VarAnnoSet UUID.
    varannoset: uuid.UUID
    #: Genome build of coordinate.
    release: str
    #: Chromosome of coordinate.
    chromosome: str
    #: Start position of entry.
    start: int
    #: End position of entry.
    end: int
    #: Reference allele.
    reference: str
    #: Alternative allele.
    alternative: str
    #: Data, the set's fields are the keys.
    payload: typing.Dict[str, str]
