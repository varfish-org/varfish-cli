"""Implementation of varfish-cli subcommand "importer *"."""

import sys
import typing
import uuid

from logzero import logger
import typer

from varfish_cli import api, common

#: The ``Typer`` instance to use for the ``cases`` sub command.
app = typer.Typer(no_args_is_help=True)


@app.command("caseimportinfo-list")
def run(
    ctx: typer.Context,
    project_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of project to list cases for")
    ],
    owner: typing.Annotated[
        typing.Optional[str],
        typer.Option("--owner", help="Optionally, name of owner to filter for"),
    ] = None,
    output_file: typing.Annotated[
        str, typer.Option("--output-file", help="Path to file to write to")
    ] = "-",
):
    # config, toml_config, args, _parser, _subparser, file=sys.stdout):
    """List case import infos."""
    common_options: common.CommonConfig = ctx.obj
    logger.info("Listing CaseImportInfo records")
    if owner:
        logger.info("- filter owner: %s" % owner)
    else:
        logger.info("- filter owner: <any>")

    res = api.case_import_info_list(
        server_url=common_options.varfish_server_url,
        api_token=common_options.varfish_api_token.get_secret_value(),
        project_uuid=project_uuid,
        owner=owner,
        verify_ssl=common_options.verify_ssl,
    )

    def do_print(file: typing.TextIO):
        print("Case Import Info List", file=file)
        print("=====================", file=file)
        print(file=file)
        if not res:
            print("No records found.", file=file)
        for info in res:
            print("- uuid: %s" % repr(str(info.sodar_uuid)), file=file)
            print("  release: %s" % repr(info.release.value), file=file)
            print("  owner: %s" % repr(info.owner), file=file)
            print("  name: %s" % repr(info.name), file=file)
            print("  index: %s" % repr(info.index), file=file)
            if info.pedigree:
                print("  members:", file=file)
                for member in info.pedigree:
                    print(
                        "    - { name: %s, father: %s, mother: %s, sex: %s, affected: %s }"
                        % tuple(
                            [
                                repr(x)
                                for x in (
                                    member.name,
                                    member.father,
                                    member.mother,
                                    member.sex,
                                    member.affected,
                                )
                            ]
                        ),
                        file=file,
                    )
            else:
                print("  members: []", file=file)
            print(file=file)
        file.flush()

    logger.info("Writing output")
    if output_file == "-":
        do_print(sys.stdout)
    else:
        with open(output_file, "wt") as outputf:
            do_print(outputf)

    logger.info("All done. Have a nice day!")
