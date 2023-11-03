"""Support for file types (for upload)."""

import enum
import pathlib
import typing
import warnings


class UnsupportedFileTypeWarning(UserWarning):
    """Warning for unsupported file types."""


@enum.unique
class FileType(enum.Enum):
    """Enumeration of supported file types."""

    #: Unknown file type.
    UNKNOWN = "UNKNOWN"

    #: MD5 checksum file.
    MD5 = "MD5"
    #: SHA1 checksum file.
    SHA1 = "SHA1"
    #: SHA256 checksum file.
    SHA256 = "SHA256"

    #: BAM file.
    BAM = "BAM"
    #: BAM index file.
    BAM_BAI = "BAM_BAI"

    #: VCF file.
    VCF = "VCF"
    #: VCF tabix index file.
    VCF_TBI = "VCF_TBI"

    #: PLINK pedigree file.
    PED = "PED"

    @property
    def is_checksum(self):
        """Return whether this is a checksum file."""
        return self in (self.MD5, self.SHA1, self.SHA256)


#: Map from file suffixes to file types.
SUFFIX_MAP = {
    ".md5": FileType.MD5,
    ".sha1": FileType.SHA1,
    ".sha256": FileType.SHA256,
    ".bam": FileType.BAM,
    ".bam.bai": FileType.BAM_BAI,
    ".vcf": FileType.VCF,
    ".vcf.gz": FileType.VCF,
    ".vcf.tbi": FileType.VCF_TBI,
    ".ped": FileType.PED,
}


def guess_by_path(path: typing.Union[str, pathlib.Path]) -> FileType:
    """File file type by path."""
    path_ = pathlib.Path(path)
    for suffix, file_type in SUFFIX_MAP.items():
        if path_.name.endswith(suffix):
            return file_type
    return FileType.UNKNOWN
