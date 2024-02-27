"""
This module defines the types used by the croco-cli
"""

from typing import Union, Callable, Any, Literal
from click import Group, Command
from click.decorators import GrpType
from typing import TypedDict, NotRequired
from github.AuthenticatedUser import AuthenticatedUser
from github.NamedUser import NamedUser

AnyCallable = Callable[..., Any]
ClickGroup = Union[Group, Callable[[AnyCallable], Union[Group, GrpType]]]
ClickCommand = Union[Callable[[Callable[..., Any]], Command], Command]


class Option(TypedDict):
    name: str
    description: NotRequired[str]
    handler: AnyCallable
    deleting_handler: NotRequired[AnyCallable]


class Package(TypedDict):
    name: str
    description: str
    version: NotRequired[str | int]


PackageSet = Literal['common', 'web3', 'selenium']


class GithubPackage(Package):
    branch: str
    access_token: NotRequired[str]


class GithubUser(TypedDict):
    data: AuthenticatedUser | NamedUser
    login: str
    name: str
    email: str
    access_token: str


class Wallet(TypedDict):
    public_key: str
    private_key: str
    mnemonic: NotRequired[str]
    current: bool
    label: str


class CustomAccount(TypedDict):
    account: str
    password: str
    email: str
    email_password: str
    current: bool
    data: NotRequired[dict[str, str]]


class EnvVariable(TypedDict):
    key: str
    value: str
