"""
Binding functions to CLI commands
"""

import click
from .utils import wrap_command
from .init import package


@click.group()
def cli():
    pass


@cli.group(help='This is command initializing a python packages and projects')
def init():
    pass


wrap_command(
    group=init,
    command=package,
    help_text='"Initialize a python package"'
)
