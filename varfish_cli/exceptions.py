"""Base exception and warning classes."""


class VarFishWarning(Warning):
    """Base warning class."""


class VarFishException(BaseException):
    """Base exception class."""


class MissingFileOnImport(BaseException):
    """Raised when not all necessary files are present during import."""


class RestApiCallException(BaseException):
    """Raised on problems with REST API calls."""


class InconsistentSamplesDataException(BaseException):
    """Raised on sample inconsistencies in files."""


class InconsistentGenomeBuild(BaseException):
    """Raised when genome builds are inconsistent."""
