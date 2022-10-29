"""Data models for supporting the VarFish CLI."""

import datetime
from enum import Enum, unique
import re
import typing
import uuid

import attr
import cattr
import dateutil.parser


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
    num_small_vars: typing.Optional[int]
    #: Number of SVs in case.
    num_svs: typing.Optional[int]


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


@unique
class EffectsV1(Enum):
    THREE_PRIME_UTR_EXON_VARIANT = "3_prime_UTR_exon_variant"
    THREE_PRIME_UTR_INTRON_VARIANT = "3_prime_UTR_intron_variant"
    FIVE_PRIME_UTR_EXON_VARIANT = "5_prime_UTR_exon_variant"
    FIVE_PRIME_UTR_INTRON_VARIANT = "5_prime_UTR_intron_variant"
    CODING_TRANSCRIPT_INTRON_VARIANT = "coding_transcript_intron_variant"
    COMPLEX_SUBSTITUTION = "complex_substitution"
    DIRECT_TANDEM_DUPLICATION = "direct_tandem_duplication"
    DISRUPTIVE_INFRAME_DELETION = "disruptive_inframe_deletion"
    DISRUPTIVE_INFRAME_INSERTION = "disruptive_inframe_insertion"
    DOWNSTREAM_GENE_VARIANT = "downstream_gene_variant"
    EXON_LOSS_VARIANT = "exon_loss_variant"
    FEATURE_TRUNCATION = "feature_truncation"
    FRAMESHIFT_ELONGATION = "frameshift_elongation"
    FRAMESHIFT_TRUNCATION = "frameshift_truncation"
    FRAMESHIFT_VARIANT = "frameshift_variant"
    INFRAME_DELETION = "inframe_deletion"
    INFRAME_INSERTION = "inframe_insertion"
    INTERGENIC_VARIANT = "intergenic_variant"
    INTERNAL_FEATURE_ELONGATION = "internal_feature_elongation"
    MISSENSE_VARIANT = "missense_variant"
    MNV = "mnv"
    NON_CODING_TRANSCRIPT_EXON_VARIANT = "non_coding_transcript_exon_variant"
    NON_CODING_TRANSCRIPT_INTRON_VARIANT = "non_coding_transcript_intron_variant"
    SLICE_ACCEPTOR_VARIANT = "splice_acceptor_variant"
    SPLICE_DONOR_VARIANT = "splice_donor_variant"
    SPLICE_REGION_VARIANT = "splice_region_variant"
    START_LOST = "start_lost"
    STOP_GAINED = "stop_gained"
    STOP_LOST = "stop_lost"
    STOP_RETAINED_VARIANT = "stop_retained_variant"
    STRUCTURAL_VARIANT = "structural_variant"
    SYNONYMOUS_VARIANT = "synonymous_variant"
    TRANSCRIPT_ABLATION = "transcript_ablation"
    UPSTREAM_GENE_VARIANT = "upstream_gene_variant"


@unique
class RecessiveModeV1(Enum):
    RECESSIVE = "recessive"
    COMPOUND_RECESSIVE = "compound-recessive"


@unique
class FailChoiceV1(Enum):
    IGNORE = "ignore"
    DROP_VARIANT = "drop-variant"
    NO_CALL = "no-call"


@unique
class GenotypeChoiceV1(Enum):
    ANY = "any"
    REF = "ref"
    HET = "het"
    HOM = "hom"
    NON_HOM = "non-hom"
    REFERENCE = "reference"
    VARIANT = "variant"
    NON_VARIANT = "non-variant"
    NON_REFERENCE = "non-reference"


@attr.s(auto_attribs=True, frozen=True)
class QualitySettingsV1:
    """Data structure to hold the information for quality settings"""

    dp_het: typing.Optional[int] = None
    dp_hom: typing.Optional[int] = None
    gq: typing.Optional[int] = None
    ab: typing.Optional[float] = None
    ad: typing.Optional[int] = None
    ad_max: typing.Optional[int] = None
    fail: FailChoiceV1 = FailChoiceV1.IGNORE


@attr.s(auto_attribs=True, frozen=True)
class RangeV1:
    """Data structure to hold a range"""

    start: int
    end: int


@attr.s(auto_attribs=True, frozen=True)
class GenomicRegionV1:
    """Data structure eto hold the information for genomic regions."""

    chromosome: str
    range: typing.Optional[RangeV1] = None

    def to_str(self):
        if not self.range:
            return self.chromosome
        else:
            return "%s:%d-%d" % (self.chromosome, self.range.start, self.range.end)


def convert_genomic_region_v1(region: GenomicRegionV1):
    if region.range:
        return (region.chromosome, region.range.start, region.range.end)
    else:
        return (region.chromosome, None, None)


@attr.s(auto_attribs=True, frozen=True)
class CaseQuerySettingsV1:
    """Data structure to hold the information for a single case query"""

    database: str

    effects: typing.List[EffectsV1]

    exac_enabled: bool
    gnomad_exomes_enabled: bool
    gnomad_genomes_enabled: bool
    thousand_genomes_enabled: bool
    inhouse_enabled: bool
    mtdb_enabled: bool
    helixmtdb_enabled: bool
    mitomap_enabled: bool

    quality: typing.Dict[str, QualitySettingsV1]
    genotype: typing.Dict[str, typing.Optional[GenotypeChoiceV1]]

    transcripts_coding: bool = True
    transcripts_noncoding: bool = False

    var_type_snv: bool = True
    var_type_indel: bool = True
    var_type_mnv: bool = True

    max_exon_dist: typing.Optional[int] = None

    flag_simple_empty: bool = True
    flag_bookmarked: bool = True
    flag_candidate: bool = True
    flag_doesnt_segregate: bool = True
    flag_final_causative: bool = True
    flag_for_validation: bool = True
    flag_no_disease_association: bool = True
    flag_segregates: bool = True

    flag_molecular_empty: bool = True
    flag_molecular_negative: bool = True
    flag_molecular_positive: bool = True
    flag_molecular_uncertain: bool = True

    flag_phenotype_match_empty: bool = True
    flag_phenotype_match_negative: bool = True
    flag_phenotype_match_positive: bool = True
    flag_phenotype_match_uncertain: bool = True

    flag_summary_empty: bool = True
    flag_summary_negative: bool = True
    flag_summary_positive: bool = True
    flag_summary_uncertain: bool = True

    flag_validation_empty: bool = True
    flag_validation_negative: bool = True
    flag_validation_positive: bool = True
    flag_validation_uncertain: bool = True

    flag_visual_empty: bool = True
    flag_visual_negative: bool = True
    flag_visual_positive: bool = True
    flag_visual_uncertain: bool = True

    gene_allowlist: typing.Optional[typing.List[str]] = None
    gene_blocklist: typing.Optional[typing.List[str]] = None
    genomic_region: typing.Optional[typing.List[GenomicRegionV1]] = None

    remove_if_in_dbsnp: bool = False

    require_in_hgmd_public: bool = False
    require_in_clinvar: bool = False
    clinvar_include_benign: bool = True
    clinvar_include_pathogenic: bool = True
    clinvar_include_likely_benign: bool = True
    clinvar_include_likely_pathogenic: bool = True
    clinvar_include_uncertain_significance: bool = True

    patho_enabled: bool = False
    patho_score: typing.Optional[str] = None

    prio_enabled: bool = False
    prio_algorithm: typing.Optional[str] = None
    prio_hpo_terms: typing.Optional[typing.List[str]] = None

    recessive_mode: typing.Optional[RecessiveModeV1] = None
    recessive_index: typing.Optional[str] = None
    denovo_index: typing.Optional[str] = None

    exac_frequency: typing.Optional[float] = None
    exac_heterozygous: typing.Optional[int] = None
    exac_homozygous: typing.Optional[int] = None
    exac_hemizygous: typing.Optional[int] = None

    gnomad_exomes_frequency: typing.Optional[float] = None
    gnomad_exomes_heterozygous: typing.Optional[int] = None
    gnomad_exomes_homozygous: typing.Optional[int] = None
    gnomad_exomes_hemizygous: typing.Optional[int] = None

    gnomad_genomes_frequency: typing.Optional[float] = None
    gnomad_genomes_heterozygous: typing.Optional[int] = None
    gnomad_genomes_homozygous: typing.Optional[int] = None
    gnomad_genomes_hemizygous: typing.Optional[int] = None

    thousand_genomes_frequency: typing.Optional[float] = None
    thousand_genomes_heterozygous: typing.Optional[int] = None
    thousand_genomes_homozygous: typing.Optional[int] = None
    thousand_genomes_hemizygous: typing.Optional[int] = None

    inhouse_carriers: typing.Optional[int] = None
    inhouse_heterozygous: typing.Optional[int] = None
    inhouse_homozygous: typing.Optional[int] = None
    inhouse_hemizygous: typing.Optional[int] = None

    mtdb_count: typing.Optional[int] = None
    mtdb_frequency: typing.Optional[float] = None

    helixmtdb_frequency: typing.Optional[float] = None
    helixmtdb_het_count: typing.Optional[int] = None
    helixmtdb_hom_count: typing.Optional[int] = None

    mitomap_count: typing.Optional[int] = None
    mitomap_frequency: typing.Optional[float] = None


@attr.s(frozen=True, auto_attribs=True)
class CaseQueryV1:
    public: bool = False
    query_settings: typing.Optional[typing.Dict[str, typing.Any]] = None
    sodar_uuid: typing.Optional[uuid.UUID] = None
    date_created: typing.Optional[datetime.datetime] = None
    user: typing.Optional[uuid.UUID] = None
    form_id: typing.Optional[str] = None
    form_version: typing.Optional[int] = None
    case: typing.Optional[uuid.UUID] = None
    name: typing.Optional[str] = None


@attr.s(frozen=True, auto_attribs=True)
class QuickPresetsV1:
    inheritance: str
    frequency: str
    impact: str
    quality: str
    chromosomes: str
    flags_etc: str
    database: str


@attr.s(frozen=True, auto_attribs=True)
class QueryShortcutsResultV1:
    presets: QuickPresetsV1
    query_settings: typing.Dict[str, typing.Any]


@attr.s(frozen=True, auto_attribs=True)
class CaseQueryResultV1:
    """Case query as returned by API."""

    sodar_uuid: uuid.UUID
    date_created: datetime.datetime
    user: uuid.UUID
    case: uuid.UUID
    form_id: str
    form_version: int
    name: typing.Optional[str]
    public: bool = False
    query_settings: typing.Optional[typing.Any] = None


@attr.s(frozen=True, auto_attribs=True)
class SmallVariantV1:
    """Small variant as returned by query result"""

    release: str
    chromosome: str
    start: int
    reference: str
    alternative: str
    var_type: str
    info: typing.Dict[str, typing.Any]
    genotype: typing.Dict[str, typing.Dict[str, typing.Any]]

    num_hom_alt: int
    num_hom_ref: int
    num_het: int
    num_hemi_alt: int
    num_hemi_ref: int
    in_clinvar: bool
    exac_frequency: int
    exac_homozygous: int
    exac_heterozygous: int
    exac_hemizygous: int
    thousand_genomes_frequency: int
    thousand_genomes_homozygous: int
    thousand_genomes_heterozygous: int
    thousand_genomes_hemizygous: int
    gnomad_exomes_frequency: int
    gnomad_exomes_homozygous: int
    gnomad_exomes_heterozygous: int
    gnomad_exomes_hemizygous: int
    gnomad_genomes_frequency: int
    gnomad_genomes_homozygous: int
    gnomad_genomes_heterozygous: int
    gnomad_genomes_hemizygous: int
    refseq_gene_id: typing.Optional[str]
    refseq_transcript_id: typing.Optional[str]
    refseq_transcript_coding: typing.Optional[bool]
    refseq_hgvs_c: typing.Optional[str]
    refseq_hgvs_p: typing.Optional[str]
    refseq_effect: typing.List[str]
    refseq_exon_dist: typing.Optional[int]
    ensembl_gene_id: typing.Optional[str]
    ensembl_transcript_id: typing.Optional[str]
    ensembl_transcript_coding: typing.Optional[bool]
    ensembl_hgvs_c: typing.Optional[str]
    ensembl_hgvs_p: typing.Optional[str]
    ensembl_effect: typing.List[str]
    ensembl_exon_dist: typing.Optional[int]


def _structure_genomic_region(s, _):
    if not re.match("^[a-zA-Z0-9]+(:(\\d+(,\\d+)*)-(\\d+(,\\d+)*))?$", s):
        raise RuntimeError("Invalid genomic region string: %s" % repr(s))
    if ":" in s:
        chrom, range = s.split(":")
        start, end = range.split("-")
        return GenomicRegionV1(chromosome=chrom, range=RangeV1(int(start), int(end)))
    else:
        return GenomicRegionV1(chromosome=s)


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
    result.register_structure_hook(GenomicRegionV1, _structure_genomic_region)
    result.register_unstructure_hook(GenomicRegionV1, GenomicRegionV1.to_str)
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
