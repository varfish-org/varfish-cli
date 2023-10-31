"""Code for parsing pedigree files."""

import re
import typing

import pydantic

#: Translation scheme for PED attribute sex to text.
SEX_MAP = {"0": "unknown", "1": "male", "2": "female"}

#: Translation scheme for PED attribute disease to text.
DISEASE_MAP = {"0": "unknown", "1": "unaffected", "2": "affected"}


class Donor(pydantic.BaseModel):
    """Represent donor from PED."""

    model_config = pydantic.ConfigDict(frozen=True)

    family_id: str
    name: str
    father_name: str
    mother_name: str
    sex: str
    disease: str


def parse_ped(ped_file) -> typing.List[Donor]:
    """Parse a given PED file and return ``Donor`` objects."""
    lines = []
    for line in ped_file.readlines():
        line = re.split(r"\s+", line.rstrip())[:6]

        if line[0].startswith("#"):
            continue

        if not len(line) == 6:  # pragma: no cover
            raise Exception("PED file not complete.")

        lines.append(
            Donor(
                family_id=line[0],
                name=line[1],
                father_name=line[2],
                mother_name=line[3],
                sex=SEX_MAP.get(line[4], "unknown"),
                disease=DISEASE_MAP.get(line[5], "unknown"),
            )
        )

    return lines
