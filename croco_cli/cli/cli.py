"""
Binding functions to CLI commands
"""

import click
from typing import cast
from .init import init
from .install import install
from croco_cli.types import ClickGroup


@click.group()
def cli():
    """
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    ░░░█████░░██████░░░█████░░░█████░░░█████░░░
    ░░██░░░██░██░░░██░██░░░██░██░░░██░██░░░██░░
    ░░██░░░░░░██████░░██░░░██░██░░░░░░██░░░██░░
    ░░██░░░██░██░░░██░██░░░██░██░░░██░██░░░██░░
    ░░░█████░░██░░░██░░█████░░░█████░░░█████░░░
    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    """


cli.add_command(cast(ClickGroup, init))
cli.add_command(cast(ClickGroup, install))
