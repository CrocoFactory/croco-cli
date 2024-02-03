"""
This module defines the types used by the croco-cli
"""

from typing import Union, Callable, Any
from click import Group, Command
from click.decorators import GrpType
from typing import TypedDict, NotRequired

AnyCallable = Callable[..., Any]
ClickGroup = Union[Group, Callable[[AnyCallable], Union[Group, GrpType]]]
ClickCommand = Union[Callable[[Callable[..., Any]], Command], Command]


class Option(TypedDict):
    name: str
    description: str
    handler: AnyCallable


class Package(TypedDict):
    name: str
    description: str
    version: NotRequired[str | int]


class GithubPackage(Package):
    branch: NotRequired[str]
    access_token: NotRequired[str]
