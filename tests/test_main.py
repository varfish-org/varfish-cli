"""Test the main function."""

import pytest

from varfish_cli.__main__ import main


def test_no_args():
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        main([])
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
