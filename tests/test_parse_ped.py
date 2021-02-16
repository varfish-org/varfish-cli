"""Tests for ``varfish_cli.parse_ped``."""

import pathlib

from varfish_cli import parse_ped


def test_parse_ped():
    base = pathlib.Path(__file__).parent
    with (base / "data/parse_ped/trio.ped").open("rt") as inputf:
        result = parse_ped.parse_ped(inputf)
    expected = [
        "Donor(family_id='FAM', name='index', father_name='father', "
        "mother_name='mother', sex='female', disease='affected')",
        "Donor(family_id='FAM', name='father', father_name='0', "
        "mother_name='0', sex='male', disease='unaffected')",
        "Donor(family_id='FAM', name='mother', father_name='0', "
        "mother_name='0', sex='female', disease='unaffected')",
    ]
    assert list(map(str, result)) == expected
