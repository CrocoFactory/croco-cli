"""
This module contains functions to install Croco Factory packages
"""

import os
import click
from functools import partial
from croco_cli.types import Option, Package, GithubPackage
from croco_cli.utils import show_key_mode
from croco_cli.globals import PYPI_PACKAGES, GITHUB_PACKAGES, GITHUB_API_TOKEN

_DESCRIPTION = "Install Croco Factory packages"


def _install_package(
        package: Package | GithubPackage,
        github_package: bool = False
) -> None:
    """
    Install Croco Factory package
    :param package: Croco Factory package
    :param github_package: Whether package is GitHub package
    :return: None
    """
    package_name = package['name']
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
        *,
        github_package: bool = False
) -> Option:
    """
    Returns an installing option for keyboard interaction mode
    :param package:
    :param github_package:
    :return: An installing option
    """
    package_name = package['name']
    description = package['description']

    if github_package:
        package['access_token'] = GITHUB_API_TOKEN
        package_name += ' (GitHub)'

    handler = partial(
        _install_package,
        package=package,
        github_package=github_package
    )

    return Option(
        name=package_name,
        description=description,
        handler=handler
    )


_PYPI_OPTIONS = [_make_install_option(package) for package in PYPI_PACKAGES]
_GITHUB_OPTIONS = [_make_install_option(package, github_package=True) for package in GITHUB_PACKAGES]
_OPTIONS = _PYPI_OPTIONS + _GITHUB_OPTIONS


def _show_install_screen() -> None:
    """
    Shows the installation packages screen
    :return: None
    """
    show_key_mode(_OPTIONS, _DESCRIPTION)


@click.command(help=_DESCRIPTION)
def install():
    _show_install_screen()

