"""
Binding functions to CLI commands
"""

import click
from typing import cast
from ._change import change
from ._init import init
from ._install import install
from ._user import user
from ._set import _set
from ._make import make
from ._reset import reset
from ._export import export
from ._import import _import
from croco_cli.types import ClickGroup


@click.group()
@click.version_option(prog_name='croco-cli', package_name='croco-cli')
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


cli.add_command(cast(ClickGroup, _import))
cli.add_command(cast(ClickGroup, export))
cli.add_command(cast(ClickGroup, change))
cli.add_command(cast(ClickGroup, init))
cli.add_command(cast(ClickGroup, install))
cli.add_command(cast(ClickGroup, user))
cli.add_command(cast(ClickGroup, _set))
cli.add_command(cast(ClickGroup, make))
cli.add_command(cast(ClickGroup, reset))
