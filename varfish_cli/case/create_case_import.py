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
    CaseImportInfo,
    DatabaseInfoFile,
    VariantSetImportState,
)
from .config import CaseCreateImportInfoConfig


#: Regular expressions of suffixes to remove.
from ..exceptions import (
    MissingFileOnImport,
    RestApiCallException,
    InconsistentSamplesDataException,
    InconsistentGenomeBuild,
)
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

    @property
    def basename(self):
        return os.path.basename(self.path)


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

        logger.info("... checking genomebuild consistency ...")
        try:
            self._check_genomebuild_consistency()
        except InconsistentGenomeBuild as e:
            self._log_exception(e)
            logger.error("Inconsistent genome builds, giving up!")
            return 1

        logger.info("... creating case import info ...")
        try:
            case_import_info = self._create_case_import_info()
        except RestApiCallException as e:
            self._log_exception(e)
            logger.error("Problem creating case import info on remote side.")
            return 1

        logger.info("... uploading files (if necessary) ...")
        good_md5s = self._upload_files(case_import_info)
        logger.info("... purging old files (if necessary) ...")
        self._purge_old_files(case_import_info, good_md5s)
        logger.info("... and updating state to 'submitted'")
        self._submit_import(case_import_info)
        return 0

    def _purge_old_files(self, case_import_info: CaseImportInfo, good_md5s: typing.Collection[str]):
        bam_qc_files = api.bam_qc_file_list(
            server_url=self.global_config.varfish_server_url,
            api_token=self.global_config.varfish_api_token,
            case_import_info_uuid=case_import_info.sodar_uuid,
            verify_ssl=self.global_config.verify_ssl,
        )
        for bam_qc_file in bam_qc_files:
            if bam_qc_file.md5 not in good_md5s:
                api.bam_qc_file_destroy(
                    server_url=self.global_config.varfish_server_url,
                    api_token=self.global_config.varfish_api_token,
                    case_import_info_uuid=case_import_info.sodar_uuid,
                    bam_qc_file_uuid=bam_qc_file.sodar_uuid,
                    verify_ssl=self.global_config.verify_ssl,
                )

        variant_sets = api.variant_set_import_info_list(
            server_url=self.global_config.varfish_server_url,
            api_token=self.global_config.varfish_api_token,
            case_import_info_uuid=case_import_info.sodar_uuid,
            verify_ssl=self.global_config.verify_ssl,
        )
        for variant_set in variant_sets:
            genotype_files = api.genotype_file_list(
                server_url=self.global_config.varfish_server_url,
                api_token=self.global_config.varfish_api_token,
                variant_set_import_info_uuid=variant_set.sodar_uuid,
                verify_ssl=self.global_config.verify_ssl,
            )
            for gt_file in genotype_files:
                if gt_file.md5 not in good_md5s:
                    api.genotype_file_destroy(
                        server_url=self.global_config.varfish_server_url,
                        api_token=self.global_config.varfish_api_token,
                        variant_set_import_info_uuid=variant_set.sodar_uuid,
                        genotype_file_uuid=gt_file.sodar_uuid,
                        verify_ssl=self.global_config.verify_ssl,
                    )
            effect_files = api.effects_file_list(
                server_url=self.global_config.varfish_server_url,
                api_token=self.global_config.varfish_api_token,
                variant_set_import_info_uuid=variant_set.sodar_uuid,
                verify_ssl=self.global_config.verify_ssl,
            )
            for eff_file in effect_files:
                if eff_file.md5 not in good_md5s:
                    api.effects_file_destroy(
                        server_url=self.global_config.varfish_server_url,
                        api_token=self.global_config.varfish_api_token,
                        variant_set_import_info_uuid=variant_set.sodar_uuid,
                        effects_file_uuid=eff_file.sodar_uuid,
                        verify_ssl=self.global_config.verify_ssl,
                    )
            db_info_files = api.db_info_file_list(
                server_url=self.global_config.varfish_server_url,
                api_token=self.global_config.varfish_api_token,
                variant_set_import_info_uuid=variant_set.sodar_uuid,
                verify_ssl=self.global_config.verify_ssl,
            )
            for db_info_file in db_info_files:
                if db_info_file.md5 not in good_md5s:
                    api.db_info_file_destroy(
                        server_url=self.global_config.varfish_server_url,
                        api_token=self.global_config.varfish_api_token,
                        variant_set_import_info_uuid=variant_set.sodar_uuid,
                        db_info_file_uuid=db_info_file.sodar_uuid,
                        verify_ssl=self.global_config.verify_ssl,
                    )

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

        guessed = []
        for key, lst in file_type_to_list.items():
            for no, path in enumerate(lst):
                if no:
                    guessed.append(["", path.basename])
                else:
                    guessed.append([key, path.basename])
        logger.info(
            "Guessed file types =\n%s",
            tabulate(guessed, headers=["file type", "file name"], tablefmt="grid"),
        )

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

    def _check_genomebuild_consistency(self):
        """Check consistency with genomebuild."""

        for path_gt in self.paths_genotype + self.paths_genotype_sv:
            if path_gt.path.endswith(".gz"):
                openf = gzip.open(path_gt.path, "rt")
            else:
                openf = open(path_gt.path, "rt")
            with openf as inputf:
                header = inputf.readline().splitlines(keepends=False)[0].split("\t")
                line = inputf.readline().splitlines(keepends=False)[0].split("\t")
                rec = dict(zip(header, line))
                if rec["release"] != self.create_config.genomebuild:
                    raise InconsistentGenomeBuild(
                        "Inconsistent genome build from file (%s): %s and from args: %s"
                        % (path_gt.path, rec["release"], self.create_config.genomebuild)
                    )

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
            verify_ssl=self.global_config.verify_ssl,
        ):
            if strip_suffix(case_info.name) == name:
                logger.info("Found existing case info: %s", case_info)
                # Make sure to update index and pedigree to current value.
                case_info = attr.assoc(case_info, index=index, pedigree=self.pedigree)
                if self.create_config.resubmit and case_info.state in (
                    CaseImportState.SUBMITTED,
                    CaseImportState.IMPORTED,
                    CaseImportState.FAILED,
                ):
                    logger.info("Case is submitted and --resubmit given, marking as draft.")
                    case_info = attr.assoc(
                        case_info,
                        release=GenomeBuild(self.create_config.genomebuild),
                        state=CaseImportState.DRAFT,
                    )
                    logger.info("Updating state existing case draft info: %s", case_info)
                    api.case_import_info_update(
                        server_url=self.global_config.varfish_server_url,
                        api_token=self.global_config.varfish_api_token,
                        project_uuid=self.create_config.project_uuid,
                        case_import_info_uuid=case_info.sodar_uuid,
                        data=case_info,
                        verify_ssl=self.global_config.verify_ssl,
                    )
                    return case_info
                elif (
                    case_info.state == CaseImportState.DRAFT and not self.create_config.force_fresh
                ):
                    logger.info("Found existing case draft info: %s", case_info)
                    return case_info
        # else: found no match
        return api.case_import_info_create(
            server_url=self.global_config.varfish_server_url,
            api_token=self.global_config.varfish_api_token,
            project_uuid=self.create_config.project_uuid,
            data=models.CaseImportInfo(
                release=GenomeBuild(self.create_config.genomebuild),
                name=name,
                index=index,
                pedigree=self.pedigree,
            ),
            verify_ssl=self.global_config.verify_ssl,
        )

    def _check_genotypes(self):
        """Check genotypes."""
        with_gts = {m.name for m in self.pedigree if m.has_gt_entries}
        for path in chain(self.paths_genotype, self.paths_genotype_sv):
            logger.debug("Checking genotype vs. pedigree samples for %s", path.path)
            dict_col = self._load_dict_col(path.path, "genotype")
            if not dict_col:
                print("INFO: empty file %s" % path.path, file=sys.stderr)
                continue
            gts = dict_col.keys()
            if gts != with_gts:
                tpl = "Inconsistent samples in %s vs. %s (exclusive %s vs. %s)"
                args = (path.path, self.path_ped.path, gts - with_gts, with_gts - gts)
                print("WARNING: %s" % (tpl % args), file=sys.stderr)

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
        try:
            handle = gzip.open(genotype_file, "rt")
        except OSError:
            handle = open(genotype_file, "rt")
        with handle as inputf:
            first_line = inputf.readline().strip()
            second_line = inputf.readline().strip()
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
            verify_ssl=self.global_config.verify_ssl,
        ):
            if file_obj.md5 == md5:
                logger.debug("- found %s with md5 %s", obj_type, md5)
                return md5
        else:  # found no match
            logger.info("- uploading %s %s", obj_type, path)
            with open(path, "rb") as handle:
                api_create_func(
                    server_url=self.global_config.varfish_server_url,
                    api_token=self.global_config.varfish_api_token,
                    **{func_uuid_arg: uuid_value},
                    data=file_type(name=os.path.basename(path), md5=md5),
                    files={"file": handle},
                    verify_ssl=self.global_config.verify_ssl,
                )
                return md5

    def _upload_files(self, case_import_info: models.CaseImportInfo):
        """Upload files where necessary."""
        # First, BAM QC files.
        good_md5s = [
            self._perform_file_upload(
                path=path.path,
                api_list_func=api.bam_qc_file_list,
                func_uuid_arg="case_import_info_uuid",
                uuid_value=case_import_info.sodar_uuid,
                obj_type="BAM QC file",
                file_type=BamQcFile,
                api_create_func=api.bam_qc_file_upload,
            )
            for path in self.paths_bam_qc
        ]

        # Match DB info files to small/large variants by file name match/mismatch.
        db_infos_small = []
        db_infos_sv = []
        db_infos_small = self.paths_database_info
        # TODO: The following is waiting for #575
        # cf.:https://cubi-gitlab.bihealth.org/CUBI_Engineering/VarFish/varfish-web/-/issues/575
        #
        # for db_info_file in self.paths_database_info:
        #     best = None
        #     best_dist = None
        #     for lst, paths in ((db_infos_small, self.paths_genotype), (db_infos_sv, self.paths_genotype_sv)):
        #         for path in paths:
        #             dist = Levenshtein.distance(db_info_file.path, path.path)
        #             if best_dist is None or best_dist > dist:
        #                 best = lst
        #                 best_dist = dist
        #     if best is not None:
        #         best.append(db_info_file)

        if self.paths_genotype:
            logger.info("- create new small variant set if necessary")
            variant_set_import_info = self._create_variant_set_import_info(
                case_import_info, CaseVariantType.SMALL
            )
            good_md5s += [
                self._perform_file_upload(
                    path=path.path,
                    api_list_func=api.genotype_file_list,
                    func_uuid_arg="variant_set_import_info_uuid",
                    uuid_value=variant_set_import_info.sodar_uuid,
                    obj_type="genotype file",
                    file_type=GenotypeFile,
                    api_create_func=api.genotype_file_upload,
                )
                for path in self.paths_genotype
            ]
            good_md5s += [
                self._perform_file_upload(
                    path=path.path,
                    api_list_func=api.db_info_file_list,
                    func_uuid_arg="variant_set_import_info_uuid",
                    uuid_value=variant_set_import_info.sodar_uuid,
                    obj_type="db info file",
                    file_type=DatabaseInfoFile,
                    api_create_func=api.db_info_file_upload,
                )
                for path in db_infos_small
            ]
            api.variant_set_import_info_update(
                server_url=self.global_config.varfish_server_url,
                api_token=self.global_config.varfish_api_token,
                case_import_info_uuid=case_import_info.sodar_uuid,
                variant_set_import_info_uuid=variant_set_import_info.sodar_uuid,
                data=attr.assoc(variant_set_import_info, state=VariantSetImportState.UPLOADED),
                verify_ssl=self.global_config.verify_ssl,
            )

        if self.paths_genotype_sv:
            logger.info("- create new structural variant set if necessary")
            variant_set_import_info = self._create_variant_set_import_info(
                case_import_info, CaseVariantType.STRUCTURAL
            )
            good_md5s += [
                self._perform_file_upload(
                    path=path.path,
                    api_list_func=api.genotype_file_list,
                    func_uuid_arg="variant_set_import_info_uuid",
                    uuid_value=variant_set_import_info.sodar_uuid,
                    obj_type="genotype file",
                    file_type=GenotypeFile,
                    api_create_func=api.genotype_file_upload,
                )
                for path in self.paths_genotype_sv
            ]
            good_md5s += [
                self._perform_file_upload(
                    path=path.path,
                    api_list_func=api.effects_file_list,
                    func_uuid_arg="variant_set_import_info_uuid",
                    uuid_value=variant_set_import_info.sodar_uuid,
                    obj_type="effects file",
                    file_type=EffectsFile,
                    api_create_func=api.effects_file_upload,
                )
                for path in self.paths_effect_sv
            ]
            good_md5s += [
                self._perform_file_upload(
                    path=path.path,
                    api_list_func=api.db_info_file_list,
                    func_uuid_arg="variant_set_import_info_uuid",
                    uuid_value=variant_set_import_info.sodar_uuid,
                    obj_type="db info file",
                    file_type=DatabaseInfoFile,
                    api_create_func=api.db_info_file_upload,
                )
                for path in db_infos_sv
            ]
            api.variant_set_import_info_update(
                server_url=self.global_config.varfish_server_url,
                api_token=self.global_config.varfish_api_token,
                case_import_info_uuid=case_import_info.sodar_uuid,
                variant_set_import_info_uuid=variant_set_import_info.sodar_uuid,
                data=attr.assoc(variant_set_import_info, state=VariantSetImportState.UPLOADED),
                verify_ssl=self.global_config.verify_ssl,
            )

        return good_md5s

    def _create_variant_set_import_info(
        self, case_import_info: models.CaseImportInfo, variant_type: CaseVariantType
    ):
        """Create variant set import info necessary."""

        for variant_set_info in api.variant_set_import_info_list(
            server_url=self.global_config.varfish_server_url,
            api_token=self.global_config.varfish_api_token,
            case_import_info_uuid=case_import_info.sodar_uuid,
            verify_ssl=self.global_config.verify_ssl,
        ):
            if not variant_set_info.variant_type == variant_type:
                continue
            if self.create_config.resubmit and variant_set_info.state in (
                VariantSetImportState.UPLOADED,
                VariantSetImportState.IMPORTED,
                VariantSetImportState.FAILED,
            ):
                logger.info("Variant set is submitted and --resubmit given, marking as draft.")
                variant_set_info = attr.assoc(
                    variant_set_info,
                    genomebuild=GenomeBuild(self.create_config.genomebuild),
                    state=VariantSetImportState.DRAFT,
                )
                logger.info("Updating state existing variant set draft info: %s", variant_set_info)
                api.variant_set_import_info_update(
                    server_url=self.global_config.varfish_server_url,
                    api_token=self.global_config.varfish_api_token,
                    case_import_info_uuid=case_import_info.sodar_uuid,
                    variant_set_import_info_uuid=variant_set_info.sodar_uuid,
                    data=variant_set_info,
                    verify_ssl=self.global_config.verify_ssl,
                )
                return variant_set_info
            elif (
                variant_set_info.state == VariantSetImportState.DRAFT
                and not self.create_config.force_fresh
            ):
                logger.info("Found existing variant_set draft info: %s", variant_set_info)
                return variant_set_info
        else:  # found no match
            return api.variant_set_import_info_create(
                server_url=self.global_config.varfish_server_url,
                api_token=self.global_config.varfish_api_token,
                case_import_info_uuid=case_import_info.sodar_uuid,
                data=models.VariantSetImportInfo(
                    genomebuild=GenomeBuild(self.create_config.genomebuild),
                    variant_type=variant_type,
                ),
                verify_ssl=self.global_config.verify_ssl,
            )

    def _submit_import(self, case_import_info: models.CaseImportInfo):
        """Submit the case import."""
        return api.case_import_info_update(
            server_url=self.global_config.varfish_server_url,
            api_token=self.global_config.varfish_api_token,
            project_uuid=self.create_config.project_uuid,
            case_import_info_uuid=case_import_info.sodar_uuid,
            data=attr.assoc(case_import_info, state=CaseImportState.SUBMITTED),
            verify_ssl=self.global_config.verify_ssl,
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
        "--force-fresh",
        default=False,
        action="store_true",
        help="Force using fresh case import even if old draft found",
    )
    parser.add_argument(
        "--resubmit",
        default=True,  # XXX
        action="store_true",
        help="Force resubmission of cases in submit state",
    )
    parser.add_argument(
        "--genomebuild",
        default="GRCh37",
        help="The genome build (GRCh37/GRCh38) of this case, defaults to GRCh37.",
        choices=("GRCh37", "GRCh38"),
    )
    parser.add_argument("project_uuid", help="UUID of the project to get.", type=uuid.UUID)
    parser.add_argument(
        "paths",
        nargs="+",
        help="Path(s) to files to use for the import. Must include PED, and annotation TSV files.",
    )


def run(config, toml_config, args, _parser, _subparser, _file=sys.stdout):
    """Run case import create command."""
    config = CaseCreateImportInfoConfig.create(args, config, toml_config)
    return CaseImporter(config).run()
