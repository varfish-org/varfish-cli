"""Test basic imports."""

import varfish_cli
from varfish_cli import __main__


def test_example():
    assert varfish_cli.__version__
