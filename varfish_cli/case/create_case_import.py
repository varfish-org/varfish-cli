"""Implementation of ``varfish-cli case create-import-info.``"""

import argparse
import enum
import gzip
import json
import os
import re
import sys
import typing
import uuid
from itertools import chain

import attr
from logzero import logger
from tabulate import tabulate

from .. import api
from ..api import (
    models,
    PedigreeMember,
    GenomeBuild,
    CaseVariantType,
    BamQcFile,
    GenotypeFile,
    EffectsFile,
    CaseImportState,
)
from .config import CaseCreateImportInfoConfig


#: Regular expressions of suffixes to remove.
from ..exceptions import MissingFileOnImport, RestApiCallException, InconsistentSamplesDataException
from ..parse_ped import parse_ped, DISEASE_MAP, SEX_MAP

REMOVE_SUFFIX_RES = (r"-N.-DNA.-.*$",)

#: Expected header for small variant genotypes.
EXPECTED_GTS = [
    "release",
    "chromosome",
    "chromosome_no",
    "start",
    "end",
    "bin",
    "reference",
    "alternative",
    "var_type",
    "case_id",
    "set_id",
    "info",
    "genotype",
    "num_hom_alt",
    "num_hom_ref",
    "num_het",
    "num_hemi_alt",
    "num_hemi_ref",
    "in_clinvar",
    "exac_frequency",
    "exac_homozygous",
    "exac_heterozygous",
    "exac_hemizygous",
    "thousand_genomes_frequency",
    "thousand_genomes_homozygous",
    "thousand_genomes_heterozygous",
    "thousand_genomes_hemizygous",
    "gnomad_exomes_frequency",
    "gnomad_exomes_homozygous",
    "gnomad_exomes_heterozygous",
    "gnomad_exomes_hemizygous",
    "gnomad_genomes_frequency",
    "gnomad_genomes_homozygous",
    "gnomad_genomes_heterozygous",
    "gnomad_genomes_hemizygous",
    "refseq_gene_id",
    "refseq_transcript_id",
    "refseq_transcript_coding",
    "refseq_hgvs_c",
    "refseq_hgvs_p",
    "refseq_effect",
    "refseq_exon_dist",
    "ensembl_gene_id",
    "ensembl_transcript_id",
    "ensembl_transcript_coding",
    "ensembl_hgvs_c",
    "ensembl_hgvs_p",
    "ensembl_effect",
    "ensembl_exon_dist",
]

#: Expected header for SV genotypes.
EXPECTED_GTS_SV = [
    "release",
    "chromosome",
    "chromosome_no",
    "start",
    "end",
    "bin",
    "start_ci_left",
    "start_ci_right",
    "end_ci_left",
    "end_ci_right",
    "case_id",
    "set_id",
    "sv_uuid",
    "caller",
    "sv_type",
    "sv_sub_type",
    "info",
    "genotype",
]

#: Expected header for SV feature effects.
EXPECTED_EFFECTS_SV = [
    "case_id",
    "set_id",
    "sv_uuid",
    "refseq_gene_id",
    "refseq_transcript_id",
    "refseq_transcript_coding",
    "refseq_effect",
    "ensembl_gene_id",
    "ensembl_transcript_id",
    "ensembl_transcript_coding",
    "ensembl_effect",
]


@attr.s(frozen=True, auto_attribs=True)
class PathWithTimestamp:
    """Helper type for storing a path with a timestamp."""

    #: The path that we have the timestamp for.
    path: str
    #: Point in time of last modification.
    mtime: float

    @classmethod
    def from_path(cls, path):
        """Construct from path."""
        return PathWithTimestamp(path, os.stat(os.path.realpath(path)).st_mtime)


class FileType(enum.Enum):
    """Enumeration for known file types."""

    #: Pedigree file.
    PED = "ped"
    #: MD5 file.
    MD5 = "md5"
    #: Database infos file.
    DB_INFOS = "db_infos"
    #: BAM QC file.
    BAM_QC = "bam_qc"
    #: Genotypes file.
    GTS = "gts"
    #: Genotypes for SVs.
    GTS_SV = "gts_sv"
    #: Feature effects for SVs.
    EFFECTS_SV = "effects_sv"


class FileTypeGuesser:
    """Helper class for implementing file type guessing."""

    def __init__(self):
        pass

    def guess(self, path) -> typing.Optional[FileType]:
        """Guess file type, return ``None`` if not successful."""
        if path.endswith(".gz"):
            with gzip.open(path, "rt") as inputf:
                return self._guess_content(inputf)
        else:
            with open(path, "rt") as inputf:
                return self._guess_content(inputf)

    def _guess_content(self, file):
        """Guess file type by content."""
        first_line = file.readline().splitlines(keepends=False)[0].split("\t")
        matchers = {
            FileType.PED: self._looks_like_ped,
            FileType.MD5: self._looks_like_md5,
            FileType.DB_INFOS: self._looks_like_db_infos,
            FileType.BAM_QC: self._looks_like_bam_qc,
            FileType.GTS: self._looks_like_gts,
            FileType.GTS_SV: self._looks_like_gts_sv,
            FileType.EFFECTS_SV: self._looks_like_effects_sv,
        }
        for file_type, func in matchers.items():
            if func(first_line):
                return file_type
        else:
            return None  # no match

    def _looks_like_ped(self, arr):
        return len(arr) == 6 and arr[4] in ("0", "1", "2") and arr[5] in ("0", "1", "2")

    def _looks_like_md5(self, arr):
        return len(arr) == 1 and re.match(r"^[a-f0-9]{32}$", arr[0].split()[0])

    def _looks_like_db_infos(self, arr):
        expected = ["genomebuild", "db_name", "release"]
        return len(arr) == 3 and arr == expected

    def _looks_like_bam_qc(self, arr):
        expected = ["case_id", "set_id", "bam_stats"]
        return len(arr) == 3 and arr == expected

    def _looks_like_gts(self, arr):
        return arr == EXPECTED_GTS

    def _looks_like_gts_sv(self, arr):
        return arr == EXPECTED_GTS_SV

    def _looks_like_effects_sv(self, arr):
        return arr == EXPECTED_EFFECTS_SV


class CaseImporter:
    """Implementation of an idempotent case importer.

    Before import, it is checked whether a case import already exists in the current project with the given name and it
    is updated if this is the case.  Otherwise, a new case import is created.  Then, for each file that is to be
    uploaded, it is checked that the file is not already present.  If it is, then it is updated if the change time
    does not match.  Otherwise, it is kept intact.  Finally, start the import by updating its status.
    """

    def __init__(self, config: CaseCreateImportInfoConfig):
        #: Configuration of ``case create`` command.
        self.create_config = config
        #: Configuration of ``case`` command.
        self.case_config = self.create_config.case_config
        #: Global CLI configuration.
        self.global_config = self.case_config.global_config

        #: The path to the pedigree file to parse.
        self.path_ped: typing.Optional[PathWithTimestamp] = None
        #: The path to the BAM QC files to import.
        self.paths_bam_qc: typing.List[PathWithTimestamp] = []
        #: The paths to the genotype TSV files for small variants.
        self.paths_genotype: typing.List[PathWithTimestamp] = []
        #: The paths to the genotype TSV files for small variants.
        self.paths_genotype_sv: typing.List[PathWithTimestamp] = []
        #: The paths to the variant effect TSV files (for structural variants only).
        self.paths_effect_sv: typing.List[PathWithTimestamp] = []
        #: The paths to the database info files to import.
        self.paths_database_info: typing.List[PathWithTimestamp] = []

        #: The pedigree members.
        self.pedigree: typing.List[PedigreeMember] = None

    def _log_exception(self, e):
        logger.exception(e, exc_info=self.global_config.verbose)

    def run(self):
        logger.info("Starting new case import ...")
        logger.info("")

        logger.info("... find out role of input paths ...")
        try:
            self._split_files_by_role()
        except MissingFileOnImport as e:
            self._log_exception(e)
            logger.error("Problem during file to role assignment, giving up!")
            return 1

        logger.info("... creating case import info ...")
        try:
            case_import_info = self._create_case_import_info()
        except RestApiCallException as e:
            self._log_exception(e)
            logger.error("Problem creating case import info on remote side.")
            return 1

        logger.info("... uploading files (if necessary) ...")
        self._upload_files(case_import_info)
        logger.info("... and updating state to 'submitted'")
        self._submit_import(case_import_info)

    def _split_files_by_role(self):
        """Split out files by their role into ``self.path_ped`` and ``self.paths_*``."""
        file_type_to_list = {
            FileType.DB_INFOS: self.paths_database_info,
            FileType.BAM_QC: self.paths_bam_qc,
            FileType.GTS: self.paths_genotype,
            FileType.GTS_SV: self.paths_genotype_sv,
            FileType.EFFECTS_SV: self.paths_effect_sv,
        }

        for path in self.create_config.paths:
            guessed = FileTypeGuesser().guess(path)
            if guessed == FileType.PED:
                if self.path_ped:
                    logger.warn("Overwriting PED path %s vs. %s", self.path_ped, path)
                self.path_ped = PathWithTimestamp.from_path(path)
            elif guessed == FileType.MD5:
                continue  # skip MD5 files for now
            elif guessed in file_type_to_list:
                file_type_to_list[guessed].append(PathWithTimestamp.from_path(path))
            else:
                logger.error("Could not assign %s of type %s", path, guessed)

        issues = []
        if not self.path_ped:
            issues.append("no PED file given")
        if len(self.paths_genotype_sv) != len(self.paths_effect_sv):
            issues.append(
                "different number of SV genotypes (%d)/effects (%d)"
                % (len(self.paths_genotype_sv), len(self.paths_effect_sv))
            )
        if not self.paths_genotype and not self.paths_genotype_sv:
            issues.append("neither small nor SVs given")
        if len(self.paths_genotype) > 1:
            logger.warn("More than one small variant genotype file given.")
        if issues:
            raise MissingFileOnImport("Problem(s) with import files: %s" % ", ".join(issues))

    def _create_case_import_info(self):
        """Create case if necessary."""

        def strip_suffix(x):
            for pattern in [self.create_config.strip_family_regex] + list(REMOVE_SUFFIX_RES):
                x = re.sub(pattern, "", x)
            return x

        name, self.pedigree = self._load_pedigree()
        index = self.pedigree[0].name
        name = strip_suffix(name)

        self._check_genotypes()
        self._check_bam_qc()

        logger.info("Case name = %s", name)
        logger.info(
            "Pedigree =\n%s",
            tabulate(
                [list(map(str, attr.astuple(m))) for m in self.pedigree],
                headers=["name", "father", "mother", "sex", "disease", "has_gts"],
                tablefmt="grid",
            ),
        )

        for case_info in api.case_import_info_list(
            server_url=self.global_config.varfish_server_url,
            api_token=self.global_config.varfish_api_token,
            project_uuid=self.create_config.project_uuid,
        ):
            if strip_suffix(case_info.name) == name:
                logger.info("Found existing case info: %s", case_info)
                if self.create_config.resubmit and case_info.state == CaseImportState.SUBMITTED:
                    logger.info("Case is submitted and --resubmit given, marking as draft.")
                    case_info = attr.assoc(case_info, state=CaseImportState.DRAFT)
                    api.case_import_info_update(
                        server_url=self.global_config.varfish_server_url,
                        api_token=self.global_config.varfish_api_token,
                        project_uuid=self.create_config.project_uuid,
                        case_import_info_uuid=case_info.sodar_uuid,
                        data=case_info,
                    )
                return case_info
        else:  # found no match
            return api.case_import_info_create(
                server_url=self.global_config.varfish_server_url,
                api_token=self.global_config.varfish_api_token,
                project_uuid=self.create_config.project_uuid,
                data=models.CaseImportInfo(name=name, index=index, pedigree=self.pedigree),
            )

    def _check_genotypes(self):
        """Check genotypes."""
        with_gts = {m.name for m in self.pedigree if m.has_gt_entries}
        for path in chain(self.paths_genotype, self.paths_genotype_sv):
            logger.debug("Checking genotype vs. pedigree samples for %s", path.path)
            gts = self._load_dict_col(path.path, "genotype").keys()
            if gts != with_gts:
                raise InconsistentSamplesDataException(
                    "Inconsistent samples in %s vs. %s (exclusive %s vs. %s)"
                    % (path.path, self.path_ped.path, gts - with_gts, with_gts - gts)
                )

    def _check_bam_qc(self):
        """Check bam_qc."""
        with_gts = {m.name for m in self.pedigree if m.has_gt_entries}
        seen_in_bam_qc = set()
        if not self.paths_bam_qc:
            logger.debug("No BAM QC found, not checking.")
            return
        for path in self.paths_bam_qc:
            logger.debug("Checking BAM QC vs. pedigree samples for %s", path.path)
            stats = self._load_dict_col(path.path, "bam_stats")
            seen_in_bam_qc |= stats.keys()
        if with_gts != seen_in_bam_qc:
            raise InconsistentSamplesDataException(
                "Inconsistencies in %s vs. %s (%s {gts only} vs. %s {bam qc only}) "
                % (
                    self.path_ped,
                    [p.path for p in self.paths_bam_qc],
                    with_gts - seen_in_bam_qc,
                    seen_in_bam_qc - with_gts,
                )
            )

    def _load_pedigree(self) -> typing.Tuple[str, typing.List[models.PedigreeMember]]:
        """Load pedigree and return pair ``(family name, pedigree list)``."""
        gts = self._load_dict_col(
            (self.paths_genotype or self.paths_genotype_sv)[0].path, "genotype"
        )
        rev_sex = {value: key for key, value in SEX_MAP.items()}
        rev_disease = {value: key for key, value in DISEASE_MAP.items()}

        case_name = None
        pedigree = []
        with open(self.path_ped.path) as inputf:
            for donor in parse_ped(inputf):
                case_name = donor.family_id
                pedigree.append(
                    models.PedigreeMember(
                        name=donor.name,
                        father=donor.father_name,
                        mother=donor.mother_name,
                        sex=int(rev_sex[donor.sex]),
                        affected=int(rev_disease[donor.disease]),
                        has_gt_entries=(gts is None or donor.name in gts),
                    )
                )

        case_name += self.create_config.case_name_suffix

        return case_name, pedigree

    def _load_dict_col(self, genotype_file, column):
        with gzip.open(genotype_file, "rt") as inputf:
            first_line = inputf.readline().splitlines(False)[0]
            second_line = inputf.readline().splitlines(False)[0]
            if not second_line:
                return None
            else:
                vals = dict(zip(first_line.split("\t"), second_line.split("\t")))
                return json.loads(vals[column].replace('"""', '"'))

    def _load_md5(self, path):
        with open(path, "rt") as inputf:
            return inputf.read().splitlines(False)[0].split()[0]

    def _perform_file_upload(
        self,
        path: str,
        api_list_func: typing.Callable,
        func_uuid_arg: str,
        uuid_value: typing.Union[str, uuid.UUID],
        obj_type: str,
        file_type: typing.Type,
        api_create_func: typing.Callable,
    ) -> typing.Any:
        """Perform file upload through the API."""
        md5 = self._load_md5(path + ".md5")
        for file_obj in api_list_func(
            server_url=self.global_config.varfish_server_url,
            api_token=self.global_config.varfish_api_token,
            **{func_uuid_arg: uuid_value},
        ):
            if file_obj.md5 == md5:
                logger.debug("- found %s with md5 %s", obj_type, md5)
                break
        else:  # found no match
            logger.info("- uploading %s %s", obj_type, path)
            with open(path, "rb") as handle:
                api_create_func(
                    server_url=self.global_config.varfish_server_url,
                    api_token=self.global_config.varfish_api_token,
                    **{func_uuid_arg: uuid_value},
                    data=file_type(name=os.path.basename(path), md5=md5),
                    files={"file": handle},
                )

    def _upload_files(self, case_import_info: models.CaseImportInfo):
        """Upload files where necessary."""
        # First, BAM QC files.
        for path in self.paths_bam_qc:
            self._perform_file_upload(
                path=path.path,
                api_list_func=api.bam_qc_file_list,
                func_uuid_arg="case_import_info_uuid",
                uuid_value=case_import_info.sodar_uuid,
                obj_type="BAM QC file",
                file_type=BamQcFile,
                api_create_func=api.bam_qc_file_upload,
            )

        if self.paths_genotype:
            logger.info("- create new small variant set if necessary")
            variant_set_import_info = self._create_variant_set_import_info(
                case_import_info, CaseVariantType.SMALL
            )
            for path in self.paths_genotype:
                self._perform_file_upload(
                    path=path.path,
                    api_list_func=api.genotype_file_list,
                    func_uuid_arg="variant_set_import_info_uuid",
                    uuid_value=variant_set_import_info.sodar_uuid,
                    obj_type="genotype file",
                    file_type=GenotypeFile,
                    api_create_func=api.genotype_file_upload,
                )

        if self.paths_genotype_sv:
            logger.info("- create new structural variant set if necessary")
            variant_set_import_info = self._create_variant_set_import_info(
                case_import_info, CaseVariantType.STRUCTURAL
            )
            for path in self.paths_genotype_sv:
                self._perform_file_upload(
                    path=path.path,
                    api_list_func=api.genotype_file_list,
                    func_uuid_arg="variant_set_import_info_uuid",
                    uuid_value=variant_set_import_info.sodar_uuid,
                    obj_type="genotype file",
                    file_type=GenotypeFile,
                    api_create_func=api.genotype_file_upload,
                )
            for path in self.paths_effect_sv:
                self._perform_file_upload(
                    path=path.path,
                    api_list_func=api.effects_file_list,
                    func_uuid_arg="variant_set_import_info_uuid",
                    uuid_value=variant_set_import_info.sodar_uuid,
                    obj_type="effects file",
                    file_type=EffectsFile,
                    api_create_func=api.effects_file_upload,
                )

    def _create_variant_set_import_info(
        self, case_import_info: models.CaseImportInfo, variant_type: CaseVariantType
    ):
        """Create variant set import info necessary."""

        for case_info in api.variant_set_import_info_list(
            server_url=self.global_config.varfish_server_url,
            api_token=self.global_config.varfish_api_token,
            case_import_info_uuid=case_import_info.sodar_uuid,
        ):
            if case_info.variant_type == variant_type:
                return case_info
        else:  # found no match
            return api.variant_set_import_info_create(
                server_url=self.global_config.varfish_server_url,
                api_token=self.global_config.varfish_api_token,
                case_import_info_uuid=case_import_info.sodar_uuid,
                data=models.VariantSetImportInfo(
                    genomebuild=GenomeBuild.GRCH37, variant_type=variant_type
                ),
            )

    def _submit_import(self, case_import_info: models.CaseImportInfo):
        """Submit the case import."""
        return api.case_import_info_update(
            server_url=self.global_config.varfish_server_url,
            api_token=self.global_config.varfish_api_token,
            project_uuid=self.create_config.project_uuid,
            case_import_info_uuid=case_import_info.sodar_uuid,
            data=attr.assoc(case_import_info, state=CaseImportState.SUBMITTED),
        )


def setup_argparse(parser):
    parser.add_argument("--hidden-cmd", dest="case_cmd", default=run, help=argparse.SUPPRESS)
    parser.add_argument(
        "--strip-family-regex",
        default="^FAM_",
        help="Regular expression to process family name with.",
    )
    parser.add_argument(
        "--case-name-suffix", type=str, default="", help="Suffix to append to case name."
    )
    parser.add_argument(
        "--resubmit",
        default=False,
        action="store_true",
        help="Also import if state is already 'submit'",
    )
    parser.add_argument("project_uuid", help="UUID of the project to get.", type=uuid.UUID)
    parser.add_argument(
        "paths",
        nargs="+",
        help="Path(s) to files to use for the import. Must include PED, and annotation TSV files.",
    )


def run(config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """Run case import create command."""
    config = CaseCreateImportInfoConfig.create(args, config, toml_config)
    return CaseImporter(config).run()
