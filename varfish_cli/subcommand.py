"""Implementation of varfish-cli subcommand."""

import argparse
from logzero import logger


def setup_argparse(parser: argparse.ArgumentParser) -> None:
    """Main entry point for subcommand."""


def run(args, parser, subparser):
    """Main entry point for subcommand command."""
    logger.info("Hello World!")
