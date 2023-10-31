"""Formal main entry point, forwards to module ``cli``."""

from varfish_cli import cli


def main():
    cli.typer_click_object()


if __name__ == "__main__":  # pragma: no cover
    main()
