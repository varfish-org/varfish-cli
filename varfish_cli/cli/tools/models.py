"""Models, e.g., for legacy bam-qc format."""

import enum
from typing import Dict, Literal, Union

from pydantic import BaseModel, ConfigDict


@enum.unique
class SummaryKey(str, enum.Enum):
    """Key for ``BamQcData.summary``."""

    #: Mean coverage
    MEAN_COVERAGE = "mean coverage"
    #: Total target size
    TOTAL_TARGET_SIZE = "total target size"


#: Literal version of ``SummaryKey``.
SummaryKeyLiteral = Literal["mean coverage", "total target size"]


@enum.unique
class BamstatsKey(str, enum.Enum):
    """Key for ``BamstatsData.summary``."""

    #: Sequences
    SEQUENCES = "sequences"
    #: Reads duplicated.
    READS_DUPLICATED = "reads duplicated"
    #: Insert size average.
    INSERT_SIZE_AVERAGE = "insert size average"
    #: Insert size standard deviation.
    INSERT_SIZE_STANDARD_DEVIATION = "insert size standard deviation"


#: Literal version of ``BamstatsKey``.
BamstatsKeyLiteral = Literal[
    "sequences", "reads duplicated", "insert size average", "insert size standard deviation"
]


class BamQcData(BaseModel):
    """Model for legacy bam-qc format."""

    model_config = ConfigDict(frozen=True)

    #: Summary information.
    summary: Dict[SummaryKeyLiteral, Union[int, float]]
    #: Mapping from min. coverage to fraction.
    min_cov_target: Dict[int, float]
    #: Information from bamstats.
    bamstats: Dict[BamstatsKeyLiteral, Union[int, float]]


class BamQc(BaseModel):
    """Model for legacy bam-qc format."""

    model_config = ConfigDict(frozen=True)

    #: Mapping from sample name to ``BamQcData``
    sample_data: Dict[str, BamQcData]
