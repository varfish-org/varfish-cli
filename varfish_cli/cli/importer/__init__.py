"""Implementation of varfish-cli subcommand "importer *"."""

import sys
import typing
import uuid

from logzero import logger
import typer

from varfish_cli import api
from varfish_cli.api import GenomeBuild
from varfish_cli.cli.importer.create import CaseImporter, CaseImportOptions
from varfish_cli.config import CommonOptions

#: The ``Typer`` instance to use for the ``importer`` sub command.
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
    """List case import infos."""
    common_options: CommonOptions = ctx.obj
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


@app.command("caseimportinfo-create")
def cli_caseimportinfo_create(
    ctx: typer.Context,
    project_uuid: typing.Annotated[
        uuid.UUID, typer.Argument(..., help="UUID of project to list cases for")
    ],
    paths: typing.Annotated[
        typing.List[str],
        typer.Argument(
            ...,
            help="Path(s) to files to use for the import. Must include PED, and annotation TSV files",
        ),
    ] = None,
    strip_family_regex: typing.Annotated[
        str,
        typer.Option("--strip-family-regex", help="Regular expression to process family name with"),
    ] = "^FAM_",
    case_name_suffix: typing.Annotated[
        str, typer.Option("--case-name-suffix", help="Suffix to append to case name")
    ] = "",
    force_fresh: typing.Annotated[
        bool,
        typer.Option(
            "--force-fresh/--no-force-fresh",
            help="Force using fresh case import even if old draft found",
        ),
    ] = False,
    resubmit: typing.Annotated[
        bool,
        typer.Option(
            "--resubmit/--no-resubmit",
            help="Force resubmission of cases in submit state",
        ),
    ] = False,
    genomebuild: typing.Annotated[
        GenomeBuild,
        typer.Option(
            "--genomebuild",
            help="The genome build (GRCh37/GRCh38) of this case, defaults to GRCh37.",
        ),
    ] = GenomeBuild.GRCH37.value,
    index: typing.Annotated[
        str,
        typer.Option(
            "--index",
            help="Name of the index case in the pedigree, "
            "defaults to the first member of the pedigree file.",
        ),
    ] = None,
):
    logger.info("Creating CaseImportInfo object...")
    common_options: CommonOptions = ctx.obj
    case_importer = CaseImporter(
        options=CaseImportOptions(
            paths=paths,
            genomebuild=genomebuild,
            strip_family_regex=strip_family_regex,
            case_name_suffix=case_name_suffix,
            force_fresh=force_fresh,
            resubmit=resubmit,
            project_uuid=project_uuid,
            index=index,
        ),
        common_options=common_options,
    )
    case_importer.run()
    logger.info("All done. Have a nice day!")
