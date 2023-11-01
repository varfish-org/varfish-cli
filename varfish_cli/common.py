"""Shared code."""

import csv
import datetime
from enum import Enum, unique
import io
import json
import typing
import uuid

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
        json.dump(output_json, output_file, cls=CustomEncoder, indent=2)
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


def load_json(path_or_payload: str) -> typing.Any:
    """Load JSON from file or string."""
    if path_or_payload.startswith("@"):
        with open(path_or_payload[1:], "rt") as inputf:
            return json.load(inputf)
    else:
        return json.loads(path_or_payload)
