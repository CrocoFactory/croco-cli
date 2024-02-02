"""
This module defines the types used by the croco-cli
"""

from typing import Union, Callable, Any
from click import Group, Command
from click.decorators import GrpType

_AnyCallable = Callable[..., Any]
ClickGroup = Union[Group, Callable[[_AnyCallable], Union[Group, GrpType]]]
ClickCommand = Union[Callable[[Callable[..., Any]], Command], Command]