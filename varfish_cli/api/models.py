"""Data models for supporting the VarFish CLI."""

from enum import Enum, unique
import typing
import uuid

import pydantic


@unique
class ProjectType(Enum):
    """Enumeration of possible project types."""

    #: Container for other categories or projects but not primary data.
    CATEGORY = "CATEGORY"
    #: Project containing primary data but no other projects.
    PROJECT = "PROJECT"


class Project(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(frozen=True)

    #: The project identifier.
    sodar_uuid: uuid.UUID
    #: Parent category UUID, if any.
    parent: typing.Optional[uuid.UUID]
    #: Project title.
    title: str
    #: Project type.
    type: ProjectType
    #: Project description.
    description: typing.Optional[str]
    #: Markdown README string.
    readme: typing.Optional[str]
    #: Whether public guest access is allowed.
    public_guest_access: bool
    #: Whether the project has been archived.
    archive: bool


class PedigreeMember(pydantic.BaseModel):
    """Represent a pedigree member as returned by the VarFish API."""

    model_config = pydantic.ConfigDict(frozen=True)

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


class Case(pydantic.BaseModel):
    """Represent a case as returned by the VarFish API."""

    model_config = pydantic.ConfigDict(frozen=True)

    #: The case identifier.
    sodar_uuid: uuid.UUID
    #: Date of creation.
    date_created: pydantic.AwareDatetime
    #: Date of last modification.
    date_modified: pydantic.AwareDatetime
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


class CaseImportInfo(pydantic.BaseModel):
    """Case import information as returned by the VarFish API."""

    model_config = pydantic.ConfigDict(frozen=True)

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
    date_created: typing.Optional[pydantic.AwareDatetime] = None
    #: Date of last modification.
    date_modified: typing.Optional[pydantic.AwareDatetime] = None
    #: UUID of the remote project
    project: typing.Optional[uuid.UUID] = None
    #: UUID of the remote case.
    case: typing.Optional[uuid.UUID] = None
    #: State.
    state: CaseImportState = CaseImportState.DRAFT
    #: Notes
    notes: typing.Optional[str] = None
    #: Tags
    tags: typing.List[str] = []


class CaseVariantType(Enum):
    """Enumeration of variant types in a case."""

    #: Small variants.
    SMALL = "SMALL"
    #: Structural variants.
    STRUCTURAL = "STRUCTURAL"


class VariantSetImportInfo(pydantic.BaseModel):
    """Information on importing a set of variants."""

    model_config = pydantic.ConfigDict(frozen=True)

    #: The genome build.
    genomebuild: GenomeBuild
    #: The variant type.
    variant_type: CaseVariantType

    #: The case identifier.
    sodar_uuid: typing.Optional[uuid.UUID] = None
    #: Date of creation.
    date_created: typing.Optional[pydantic.AwareDatetime] = None
    #: Date of last modification.
    date_modified: typing.Optional[pydantic.AwareDatetime] = None
    #: UUID of the linked ``CaseImportInfo``.
    case_import_info: typing.Optional[uuid.UUID] = None
    #: State.
    state: VariantSetImportState = VariantSetImportState.DRAFT


class BamQcFile(pydantic.BaseModel):
    """Information for BAM QC file without the payload."""

    model_config = pydantic.ConfigDict(frozen=True)

    #: Name of the file.
    name: str
    #: MD5 sum of the file.
    md5: str

    #: The case identifier.
    sodar_uuid: typing.Optional[uuid.UUID] = None
    #: Date of creation.
    date_created: typing.Optional[pydantic.AwareDatetime] = None
    #: Date of last modification.
    date_modified: typing.Optional[pydantic.AwareDatetime] = None
    #: UUID of the linked ``CaseImportInfo``.
    case_import_info: typing.Optional[uuid.UUID] = None


class CaseGeneAnnotationFile(pydantic.BaseModel):
    """Information for Gene Annotation file without the payload."""

    model_config = pydantic.ConfigDict(frozen=True)

    #: Name of the file.
    name: str
    #: MD5 sum of the file.
    md5: str

    #: The case identifier.
    sodar_uuid: typing.Optional[uuid.UUID] = None
    #: Date of creation.
    date_created: typing.Optional[pydantic.AwareDatetime] = None
    #: Date of last modification.
    date_modified: typing.Optional[pydantic.AwareDatetime] = None
    #: UUID of the linked ``CaseImportInfo``.
    case_import_info: typing.Optional[uuid.UUID] = None


class GenotypeFile(pydantic.BaseModel):
    """Genotype file."""

    model_config = pydantic.ConfigDict(frozen=True)

    #: Name of the file.
    name: str
    #: MD5 sum of the file.
    md5: str

    #: The case identifier.
    sodar_uuid: typing.Optional[uuid.UUID] = None
    #: Date of creation.
    date_created: typing.Optional[pydantic.AwareDatetime] = None
    #: Date of last modification.
    date_modified: typing.Optional[pydantic.AwareDatetime] = None
    #: UUID of the linked ``CaseImportInfo``.
    case_import_info: typing.Optional[uuid.UUID] = None


class EffectsFile(pydantic.BaseModel):
    """Effects file."""

    model_config = pydantic.ConfigDict(frozen=True)

    #: Name of the file.
    name: str
    #: MD5 sum of the file.
    md5: str

    #: The case identifier.
    sodar_uuid: typing.Optional[uuid.UUID] = None
    #: Date of creation.
    date_created: typing.Optional[pydantic.AwareDatetime] = None
    #: Date of last modification.
    date_modified: typing.Optional[pydantic.AwareDatetime] = None
    #: UUID of the linked ``CaseImportInfo``.
    case_import_info: typing.Optional[uuid.UUID] = None


class DatabaseInfoFile(pydantic.BaseModel):
    """Database information file."""

    model_config = pydantic.ConfigDict(frozen=True)

    #: Name of the file.
    name: str
    #: MD5 sum of the file.
    md5: str

    #: The case identifier.
    sodar_uuid: typing.Optional[uuid.UUID] = None
    #: Date of creation.
    date_created: typing.Optional[pydantic.AwareDatetime] = None
    #: Date of last modification.
    date_modified: typing.Optional[pydantic.AwareDatetime] = None
    #: UUID of the linked ``CaseImportInfo``.
    case_import_info: typing.Optional[uuid.UUID] = None


class VarAnnoSetV1(pydantic.BaseModel):
    """VarAnnoSet as returned by query result"""

    model_config = pydantic.ConfigDict(frozen=True)

    #: The case identifier.
    sodar_uuid: uuid.UUID
    #: Date of creation.
    date_created: pydantic.AwareDatetime
    #: Date of last modification.
    date_modified: pydantic.AwareDatetime

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


class VarAnnoSetEntryV1(pydantic.BaseModel):
    """VarAnnoSet as returned by query result"""

    #: The case identifier.
    sodar_uuid: uuid.UUID
    #: Date of creation.
    date_created: pydantic.AwareDatetime
    #: Date of last modification.
    date_modified: pydantic.AwareDatetime

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


class SettingsEntry(pydantic.BaseModel):
    """Configuration entry from server"""

    #: Project UUID.
    project: typing.Optional[uuid.UUID]
    #: User UUID, if any.
    user: typing.Optional[uuid.UUID]
    #: Name of the app.
    app_name: str
    #: Name of the setting.
    name: str
    #: Type of the setting.
    type: typing.Literal["STRING", "INTEGER", "BOOLEAN"]
    #: Value of the setting.
    value: typing.Any
    #: Whether the user can modify the setting.
    user_modifiable: bool
