"""Shared code."""

import csv
import datetime
from enum import Enum, unique
import io
import json
import typing
import uuid

import attr
from tabulate import tabulate


class CustomEncoder(json.JSONEncoder):
    """JSON encoder for UUIds"""

    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # If the obj is uuid, we simply return the value of uuid
            return obj.hex
        elif isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        elif isinstance(obj, Enum):
            return obj.value
        else:
            # Default implementation raises not-serializable TypeError exception
            return json.JSONEncoder.default(self, obj)  # pragma: no cover


@unique
class OutputFormat(Enum):
    TABLE = "table"
    CSV = "csv"
    JSON = "json"


@attr.s(frozen=True, auto_attribs=True)
class CommonConfig:
    """Common configuration for all commands."""

    #: Verbose mode activated
    verbose: bool

    #: Whether to enable SSL verification in HTTPS requests.
    verify_ssl: bool

    #: API key to use for VarFish.
    varfish_api_token: str = attr.ib(repr=lambda value: repr(value[:4] + (len(value) - 4) * "*"))

    #: Base URL to VarFish server.
    varfish_server_url: str

    @staticmethod
    def create(args, toml_config=None):
        toml_config = toml_config or {}
        return CommonConfig(
            verbose=args.verbose,
            verify_ssl=args.verify_ssl,
            varfish_api_token=(
                args.varfish_api_token or toml_config.get("global", {}).get("varfish_api_token")
            ),
            varfish_server_url=(
                args.varfish_server_url or toml_config.get("global", {}).get("varfish_server_url")
            ),
        )


def run_nocmd(_config, _toml_config, _args, parser, subparser=None):  # pragma: no cover
    """No command given, print help and ``exit(1)``."""
    if subparser:
        subparser.print_help()
        subparser.exit(1)
    else:
        parser.print_help()
        parser.exit(1)


def write_output(
    output: typing.List[typing.List[typing.Any]],
    output_file: io.TextIOBase,
    output_format: OutputFormat,
    delimiter: str,
):
    """Write output to ``output_file``"""
    if output_format == OutputFormat.CSV:
        writer = csv.writer(output_file, delimiter=delimiter)
        for row in output:
            writer.writerow(row)
    elif output_format == OutputFormat.JSON:
        header = output[0]
        output_json = []
        for obj in output[1:]:
            output_json.append(dict(zip(header, obj)))
        json.dump(output_json, output_file, cls=CustomEncoder)
    else:
        output_file.write(tabulate(output[1:], headers=output[0], tablefmt="grid"))
    output_file.write("\n")
    output_file.flush()


def tabular_output(
    values: typing.List[typing.Any],
    header: typing.List[str],
    field_formatters: typing.Dict[str, typing.Callable[[typing.Any], str]] = {},
) -> typing.List[typing.List[str]]:
    """Convert list of values to list of strings for output."""
    output = [header]
    for value in values:
        row = []
        for field in header:
            if field in field_formatters:
                the_value = field_formatters[field](value)
            else:
                the_value = getattr(value, field)
            row.append(the_value)
        output.append(row)
    return output


def strip_trailing_slash(s: str) -> str:
    while s.endswith("/"):
        s = s[:-1]
    return s
