"""Common code for the CLI."""

import json
import typing
import uuid
import sys
import attrs

import pydantic
from logzero import logger
from varfish_cli import api, common, config

from varfish_cli.common import OutputFormat


class ListObjects(pydantic.BaseModel):
    """Utility class for listing objects."""

    #: Any common options.
    common_options: config.CommonOptions
    #: The wrapped type.
    typ: type
    #: Default fields to use for each output format.
    default_fields: typing.Dict[OutputFormat, typing.Optional[typing.Tuple[str, ...]]]
    #: The callable
    callable: typing.Callable
    #: Optionally, the related project UUID.
    project_uuid: typing.Optional[uuid.UUID] = None

    def run(
        self,
        output_file: str,
        output_format: OutputFormat,
        output_delimiter: str,
        output_fields: typing.List[str],
    ):
        all_fields = [f.name for f in attrs.fields(self.typ)]
        output_fields: typing.List[str] = (
            output_fields or self.default_fields.get(output_format) or all_fields
        )

        logger.info(f"Listing {self.typ} records")
        kwargs = {}
        if self.project_uuid:
            kwargs["project_uuid"] = self.project_uuid
        res = self.callable(
            server_url=self.common_options.varfish_server_url,
            api_token=self.common_options.varfish_api_token.get_secret_value(),
            verify_ssl=self.common_options.verify_ssl,
            **kwargs,
        )

        logger.info("Generating output")
        header = (
            output_fields if output_fields else [f.name for f in attrs.fields(api.VarAnnoSetV1)]
        )
        output = common.tabular_output(values=res, header=header)

        logger.info("Writing output")
        logger.info("==============")
        if output_file == "-":
            common.write_output(
                output,
                sys.stdout,
                output_format,
                output_delimiter,
            )
        else:
            with open(output_file, "wt") as outputf:
                common.write_output(
                    output,
                    outputf,
                    output_format,
                    output_delimiter,
                )
        logger.info("All done. Have a nice day!")


class RetrieveObject(pydantic.BaseModel):
    """Utility class to retrieve one object."""

    #: Any common options.
    common_options: config.CommonOptions
    #: The wrapped type.
    typ: type
    #: The callable
    callable: typing.Callable
    #: The name of the key
    key_name: str
    #: The object UUID
    object_uuid: uuid.UUID

    def run(
        self,
        output_file: str,
    ):
        logger.info("Configuration: %s", config)
        logger.info(f"Retrieving {self.typ} object")
        kwargs = {
            self.key_name: self.object_uuid
        }
        res = self.callable(
            server_url=self.common_options.varfish_server_url,
            api_token=self.common_options.varfish_api_token.get_secret_value(),
            verify_ssl=self.common_options.verify_ssl,
            **kwargs,
        )
        res_json = api.CONVERTER.unstructure(res)

        logger.info(f"{self.typ} Detail")
        logger.info("============" + "=" * len(str(self.typ)))
        if output_file == "-":
            json.dump(res_json, sys.stdout, indent=2)
            sys.stdout.write("\n")
            sys.stdout.flush()
        else:
            with open(output_file, "wt") as outputf:
                json.dump(res_json, outputf, indent=2)
                outputf.write("\n")
        logger.info("All done. Have a nice day!")
