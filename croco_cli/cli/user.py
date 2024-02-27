import json
import click
from croco_cli.database import database
from croco_cli.types import CustomAccount
from croco_cli.utils import require_github, show_detail, show_label, hide_value, show_account_dict, show_wallets, echo_error


@click.command()
@click.option(
    '-g',
    '--git',
    help='Show GitHub user account',
    show_default=True,
    is_flag=True,
    default=True
)
@click.option(
    '-w',
    '--wallets',
    help='Show wallets of user',
    show_default=True,
    is_flag=True,
    default=False
)
@click.option(
    '-c',
    '--custom',
    help='Show custom accounts of user',
    show_default=True,
    is_flag=True,
    default=False
)
@require_github
def user(git: bool, wallets: bool, custom: bool) -> None:
    """Show user accounts"""
    if wallets:
        show_wallets()
    elif custom:
        _show_custom_accounts()
    elif git:
        _show_github()


def _show_github() -> None:
    """Show GitHub user account"""
    github_user = database.get_github_user()
    access_token = hide_value(github_user['access_token'], 10)
    show_label('GitHub')
    show_detail('Login', github_user["login"])
    show_detail('Email', github_user["email"])
    show_detail('Access token', access_token)


def _show_custom_account(custom_account: CustomAccount) -> None:
    """Show custom accounts of user"""
    custom_data = custom_account.pop('data')
    current = custom_account.pop('current')
    if isinstance(custom_data, str):
        custom_data = json.loads(custom_data)

    label = f'{custom_account.pop("account").capitalize()} (Current)' if current else custom_account.pop('account').capitalize()
    show_account_dict(custom_account, label)

    custom_data and show_account_dict(custom_data)


def _show_custom_accounts() -> None:
    """Show custom accounts of user"""
    if not database.custom_accounts.table_exists():
        echo_error('There are no custom accounts to show')
        return

    custom_accounts = database.get_custom_accounts()
    if not custom_accounts:
        echo_error('There are no custom accounts to show')
        return

    for custom_account in custom_accounts:
        _show_custom_account(custom_account)
