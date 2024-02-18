"""
Binding functions to CLI commands
"""

import click
from typing import cast
from .change import change
from .init import init
from .install import install
from .user import user
from .set import _set
from .make import make
from .reset import reset
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


cli.add_command(cast(ClickGroup, change))
cli.add_command(cast(ClickGroup, init))
cli.add_command(cast(ClickGroup, install))
cli.add_command(cast(ClickGroup, user))
cli.add_command(cast(ClickGroup, _set))
cli.add_command(cast(ClickGroup, make))
cli.add_command(cast(ClickGroup, reset))
