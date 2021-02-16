import datetime
import pathlib
import uuid

import cattr
import requests_mock

from varfish_cli.__main__ import main
from varfish_cli.api import models


def test_run_case_list():
    url = "https://varfish.example.com"
    address = "%s/variants/api/case/c3752df7-fa32-4784-8a48-e8f0e5a28790/" % url
    cases = cattr.unstructure(
        [
            models.Case(
                sodar_uuid=str(uuid.uuid4()),
                date_created=datetime.datetime.now().isoformat(),
                date_modified=datetime.datetime.now().isoformat(),
                name="Case_Name",
                index="index",
                pedigree=[
                    models.PedigreeMember(
                        name="index", father="0", mother="0", sex=2, affected=2, has_gt_entries=True
                    )
                ],
                num_small_vars=123,
                num_svs=456,
            )
        ]
    )
    with requests_mock.Mocker() as m:
        m.get(address, json=cases)
        base_dir = pathlib.Path(__file__).parent
        main(
            [
                "--config",
                str(base_dir / "data/config/varfishrc.toml"),
                "case",
                "list",
                "c3752df7-fa32-4784-8a48-e8f0e5a28790",
            ]
        )
