"""
Utility functions for croco-cli
"""
import os
import re
import subprocess
import blessed
import click
from requests.adapters import ConnectionError
from typing import Callable
from croco_cli._database import Database
from croco_cli.exceptions import PoetryNotFoundException, InvalidToken, InvalidMnemonic
from croco_cli.types import Wallet, Package, GithubPackage
from functools import wraps
from .tools import Echo

_term = blessed.Terminal()


def snake_case(s: str) -> str:
    """
    Convert a string to snake_case.
    """
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    s = re.sub(r'\W+', '_', s).lower()
    s = re.sub(r'_+', '_', s)
    return s


def constant_case(s: str) -> str:
    """
    Convert a string to CONSTANT_CASE.
    """
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    s = re.sub(r'\W+', '_', s)
    return s.upper()


def is_github_package(package: Package | GithubPackage) -> bool:
    """
    Check if a package is a GitHub package
    :param package: The package to check
    :return: True if the package is a GitHub package, false otherwise
    """
    return bool(package.get('branch'))


def require_github(func: Callable):
    """
    Decorator to require a GitHub API token in order to run the command.

    :param func: The function to be decorated.
    :return: The decorated function.
    """
    database = Database()

    @wraps(func)
    @catch_github_errors
    def wrapper(*args, **kwargs):
        if not database.get_github_user():
            env_token = os.environ.get("CROCO_GIT_TOKEN")

            if env_token:
                database.set_github_user(env_token)
            else:
                Echo.warning('GitHub access token is missing. Set it to continue')
                token = click.prompt('', hide_input=True)
                database.set_github_user(token)

        return func(*args, **kwargs)

    return wrapper


def require_wallet(func: Callable):
    """
    Decorator to require a Wallet in order to run the command.

    :param func: The function to be decorated.
    :return: The decorated function.
    """
    database = Database()

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not database.wallets.table_exists():
            env_token = os.environ.get("CROCO_WALLET_KEY")
            if env_token:
                database.set_wallet(env_token)
                return func(*args, **kwargs)
            else:
                Echo.warning('Wallet private key is missing. Set it to continue (croco set wallet).')
        else:
            return func(*args, **kwargs)

    return wrapper


def sort_wallets(wallets: list[Wallet]) -> list[Wallet]:
    """
    Sort a list of wallets.

    :param wallets: List of wallets to be sorted.
    :return: Sorted list of wallets.
    """
    wallet_number = 1
    for wallet in wallets:
        label = wallet["label"]
        if not label:
            label = f'Wallet {wallet_number}'
            wallet_number += 1

        wallet['label'] = label

    def sort_by_key(item: Wallet) -> str:
        if item['current']:
            return chr(0)
        else:
            return item['label']

    wallets = sorted(wallets, key=sort_by_key)
    return wallets


def hide_value(value: str, begin_part: int, end_part: int = 8) -> str:
    """
    Hide part of the value, replacing it with *.

    :param value: The original value.
    :param begin_part: The number of characters to show at the beginning.
    :param end_part: The number of characters to show at the end.
    :return: The modified value with hidden parts.
    """
    value = value[:begin_part] + '****...' + value[-end_part:]
    return value


def get_poetry_version() -> str:
    result = subprocess.run('poetry --version', shell=True, capture_output=True, text=True)
    if result.returncode != 0 or 'is not recognized' in result.stderr or 'is not recognized' in result.stdout:
        raise PoetryNotFoundException
    else:
        version = result.stdout.split('version')[1].split(')')[0].strip()
        return version


def check_poetry(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            get_poetry_version()
        except PoetryNotFoundException as ex:
            Echo.error(str(ex))
        else:
            return func(*args, **kwargs)

    return wrapper


def catch_github_errors(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except InvalidToken as err:
            Echo.error(str(err))
            return
        except ConnectionError:
            Echo.error('Unable to connect to GitHub account')
            return
        else:
            return result

    return wrapper


def catch_wallet_errors(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except InvalidMnemonic as err:
            Echo.error(str(err))
            return
        else:
            return result

    return wrapper


@check_poetry
def run_poetry_command(command: str) -> None:
    os.system(command)
