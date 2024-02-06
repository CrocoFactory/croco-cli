from typing import Optional

import click
from croco_cli.globals import DATABASE
from croco_cli.types import Wallet
from croco_cli.utils import require_github, sort_wallets


@click.command()
@click.option(
    '--git',
    help='Show GitHub user account',
    show_default=True,
    is_flag=True,
    default=True
)
@click.option(
    '--wallets',
    help='Show wallets of user',
    show_default=True,
    is_flag=True,
    default=False
)
@require_github
def user(git: bool, wallets: bool) -> None:
    """Show user accounts"""
    if wallets:
        _show_wallets()
        return
    if git:
        _show_github()


def _show_label(label: str, padding: Optional[int] = 0) -> None:
    padding = '     ' * padding
    click.echo(click.style(f'{padding}[{label}]', fg='blue', bold=True))


def _show_detail(key: str, value: str, padding: Optional[int] = 1) -> None:
    padding = '     ' * padding
    click.echo(click.style(f'{padding}{key}: ', fg='magenta'), nl=False)
    click.echo(click.style(f'{value}', fg='green'))


def _hide_value(value: str, begin_part: int, end_part: int = 8) -> str:
    value = value[:begin_part] + '****...' + value[-end_part:]
    return value


def _show_github() -> None:
    """Show GitHub user account"""
    github_user = DATABASE.get_github_user()
    access_token = _hide_value(github_user['access_token'], 10)
    _show_label('GitHub')
    _show_detail('Login', github_user["login"])
    _show_detail('Email', github_user["email"])
    _show_detail('Access token', access_token)


def _show_wallets() -> None:
    """Show wallets of user"""
    wallets = DATABASE.get_wallets()
    wallets = sort_wallets(wallets)
    for wallet in wallets:
        label = f'{wallet["label"]} (Current)' if wallet["current"] else wallet['label']

        private_key = _hide_value(wallet["private_key"], 5, 5)
        _show_label(f'{label}')
        _show_detail('Public Key', wallet['public_key'])
        _show_detail('Private Key', private_key)
