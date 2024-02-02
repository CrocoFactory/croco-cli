"""
Utility functions for croco-cli
"""

import re
from functools import wraps
from typing import Callable
from croco_cli.types import ClickGroup, ClickCommand


def snake_case(s: str) -> str:
    """
    Convert a string to snake_case.
    """
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    s = re.sub(r'\W+', '_', s).lower()
    s = re.sub(r'_+', '_', s)
    return s


def wrap_command(
        group: ClickGroup,
        command: Callable,
        *,
        help_text: str
) -> ClickCommand:
    """
    Wraps a command in a click group
    :param group: The click group
    :param command: The command represented as Callable. It must not be wrapped in a click group before calling this function
    :param help_text: The help text of the command
    :return: The wrapped command
    """
    @group.command(help=help_text)
    @wraps(command)
    def wrapper(*args, **kwargs):
        return command(*args, **kwargs)

    return wrapper
