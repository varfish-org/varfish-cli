"""Common code for the CLI."""

import json
import sys
import typing
import uuid

import attrs
from logzero import logger

from varfish_cli import api, common, config
from varfish_cli.common import OutputFormat

#: Type to use for model in the helper classes below.
ModelType = typing.TypeVar("ModelType", bound=object)


class ListObjects(typing.Generic[ModelType]):
    """Utility class for listing objects."""

    def __init__(self, model: typing.Type[ModelType]):
        self.model = model

    def run(
        self,
        common_options: config.CommonOptions,
        callable: typing.Callable,
        output_file: str,
        output_format: OutputFormat,
        output_delimiter: str,
        default_fields: typing.Dict[str, typing.Optional[typing.Tuple[str, ...]]],
        output_fields: typing.Optional[typing.List[str]] = None,
        project_uuid: typing.Optional[uuid.UUID] = None,
    ):
        all_fields = [f.name for f in attrs.fields(self.model)]
        output_fields: typing.List[str] = (
            output_fields or default_fields.get(output_format.value) or all_fields
        )

        logger.info(f"Listing {self.model.__name__} records")
        kwargs = {}
        if project_uuid:
            kwargs["project_uuid"] = project_uuid
        logger.info(
            "args = %s",
            (
                common_options.varfish_server_url,
                common_options.varfish_api_token.get_secret_value(),
                common_options.verify_ssl,
            ),
        )
        res = callable(
            server_url=common_options.varfish_server_url,
            api_token=common_options.varfish_api_token.get_secret_value(),
            verify_ssl=common_options.verify_ssl,
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


class RetrieveObject(typing.Generic[ModelType]):
    """Utility class to retrieve one object."""

    def __init__(self, model: typing.Type[ModelType]):
        self.model = model

    def run(
        self,
        common_options: config.CommonOptions,
        callable: typing.Callable,
        key_name: str,
        object_uuid: uuid.UUID,
        output_file: str,
    ):
        logger.info("Configuration: %s", config)
        logger.info(f"Retrieving {self.model.__name__} object")
        kwargs = {key_name: object_uuid}
        res = callable(
            server_url=common_options.varfish_server_url,
            api_token=common_options.varfish_api_token.get_secret_value(),
            verify_ssl=common_options.verify_ssl,
            **kwargs,
        )
        res_json = api.CONVERTER.unstructure(res)

        logger.info(f"{self.model.__name__} Detail")
        logger.info("============" + "=" * len(str(self.model.__name__)))
        if output_file == "-":
            json.dump(res_json, sys.stdout, indent=2)
            sys.stdout.write("\n")
            sys.stdout.flush()
        else:
            with open(output_file, "wt") as outputf:
                json.dump(res_json, outputf, indent=2)
                outputf.write("\n")
        logger.info("All done. Have a nice day!")


class CreateObject(typing.Generic[ModelType]):
    """Utility class to create one object."""

    def __init__(self, model: typing.Type[ModelType]):
        self.model = model

    def run(
        self,
        common_options: config.CommonOptions,
        callable: typing.Callable,
        parent_key_name: str,
        parent_uuid: uuid.UUID,
        payload: typing.Any,
        output_file: str,
    ):
        logger.info("Configuration: %s", config)
        logger.info(f"Creating {self.model.__name__} object")
        kwargs = {parent_key_name: parent_uuid}
        res = callable(
            server_url=common_options.varfish_server_url,
            api_token=common_options.varfish_api_token.get_secret_value(),
            verify_ssl=common_options.verify_ssl,
            payload=payload,
            **kwargs,
        )
        print(res)
        res_json = api.CONVERTER.unstructure(res)

        logger.info(f"{self.model.__name__} Detail")
        logger.info("============" + "=" * len(str(self.model.__name__)))
        if output_file == "-":
            json.dump(res_json, sys.stdout, indent=2)
            sys.stdout.write("\n")
            sys.stdout.flush()
        else:
            with open(output_file, "wt") as outputf:
                json.dump(res_json, outputf, indent=2)
                outputf.write("\n")
        logger.info("All done. Have a nice day!")


class UpdateObject(typing.Generic[ModelType]):
    """Utility class to update one object."""

    def __init__(self, model: typing.Type[ModelType]):
        self.model = model

    def run(
        self,
        common_options: config.CommonOptions,
        callable: typing.Callable,
        object_key_name: str,
        object_uuid: uuid.UUID,
        payload: typing.Any,
        output_file: str,
    ):
        logger.info("Configuration: %s", config)
        logger.info(f"Updating {self.model.__name__} object")
        kwargs = {object_key_name: object_uuid}
        res = callable(
            server_url=common_options.varfish_server_url,
            api_token=common_options.varfish_api_token.get_secret_value(),
            verify_ssl=common_options.verify_ssl,
            payload=payload,
            **kwargs,
        )
        res_json = api.CONVERTER.unstructure(res)

        logger.info(f"{self.model.__name__} Detail")
        logger.info("============" + "=" * len(str(self.model.__name__)))
        if output_file == "-":
            json.dump(res_json, sys.stdout, indent=2)
            sys.stdout.write("\n")
            sys.stdout.flush()
        else:
            with open(output_file, "wt") as outputf:
                json.dump(res_json, outputf, indent=2)
                outputf.write("\n")
        logger.info("All done. Have a nice day!")
