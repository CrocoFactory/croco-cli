"""
This module contains functions to install Croco Factory packages
"""

import os
import click
from functools import partial
from croco_cli.types import Option, Package, GithubPackage, PackageSet
from croco_cli.utils import show_key_mode, require_github, is_github_package
from croco_cli.globals import PYPI_PACKAGES, GITHUB_PACKAGES, PACKAGE_SETS
from croco_cli.database import database

_DESCRIPTION = "Install Croco Factory packages"


def _install_package(
        package: Package | GithubPackage
) -> None:
    """
    Install Croco Factory package
    :param package: Croco Factory package
    :return: None
    """
    package_name = package['name']
    github_package = is_github_package(package)
    if not github_package:
        command = f"poetry add {package_name}"
    else:
        token = package.get('access_token')
        branch = package.get('branch')
        if token:
            command = f"poetry add git+https://{token}@github.com/blnkoff/{package_name}.git"
        else:
            command = f"poetry add git+https://github.com/blnkoff/{package_name}.git"

        if branch:
            command += f"@{branch}"

    os.system(command)


def _make_install_option(
        package: Package | GithubPackage,
) -> Option:
    """
    Returns an installing option for keyboard interaction mode
    :param package: package to install
    :return: An installing option
    """
    github_user = database.get_github_user()
    package_name = package['name']
    description = package['description']
    github_package = is_github_package(package)

    if github_package:
        package['access_token'] = github_user['access_token']
        package_name += ' (GitHub)'

    handler = partial(
        _install_package,
        package=package
    )

    return Option(
        name=package_name,
        description=description,
        handler=handler
    )


def _make_set_install_option(
        package_set: PackageSet
) -> Option:
    """
    Returns an installing option for keyboard interaction mode
    :param package_set: package set to install
    :return: An installing option
    """
    set_map = PACKAGE_SETS[package_set]
    handlers = [partial(_install_package, package) for package in set_map['packages']]

    def handler():
        for handler in handlers:
            handler()

    return Option(
        name=package_set,
        description=set_map['description'],
        handler=handler
    )


def _get_options(set_mode: bool) -> list[Option]:
    """
    Gets an installing options for keyboard interaction
    :param set_mode: whether to use package sets
    """
    if not set_mode:
        pypi_options = [_make_install_option(package) for package in PYPI_PACKAGES]
        github_options = [_make_install_option(package) for package in GITHUB_PACKAGES]
        options = pypi_options + github_options
    else:
        options = [_make_set_install_option(package_set) for package_set in PACKAGE_SETS.keys()]

    return options


def _show_install_screen(set_mode: bool) -> None:
    """
    Shows the installation packages screen
    :return: None
    """
    options = _get_options(set_mode)
    show_key_mode(options, _DESCRIPTION)


@click.command(help=_DESCRIPTION)
@click.option(
    '-s',
    '--set',
    'set_',
    help='Install sets of packages',
    show_default=True,
    is_flag=True,
    default=False
)
@require_github
def install(set_: bool):
    _show_install_screen(set_)
