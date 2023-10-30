import typing

import attr

from varfish_cli.common import CommonConfig, OutputFormat


@attr.s(frozen=True, auto_attribs=True)
class ProjectsConfig:
    """Configuration for the ``varfish-cli project`` command."""

    #: Global configuration
    global_config: CommonConfig

    #: Path to output file
    output_file: str = "-"

    #: Output format
    output_format: OutputFormat = OutputFormat.TABLE

    #: delimiter for CSV output
    output_delimiter: str = ","

    #: Fields to use for output.
    output_fields: typing.Optional[typing.List[str]] = []

    @staticmethod
    def create(args, global_config, toml_config=None):
        _ = toml_config
        return ProjectsConfig(
            output_format=OutputFormat(args.output_format),
            output_file=args.output_file,
            output_delimiter=args.output_delimiter,
            output_fields=args.output_fields.split(",") if args.output_fields else [],
            global_config=global_config,
        )


@attr.s(frozen=True, auto_attribs=True)
class ProjectsListConfig:
    """Configuration for the ``varfish-cli projects project-list`` command."""

    #: Project configuration
    projects_config: ProjectsConfig

    @staticmethod
    def create(args, projects_config, toml_config=None):
        _ = args
        _ = toml_config
        return ProjectsListConfig(
            projects_config=projects_config,
        )
