import click
from typing import Optional
from croco_cli.database import database
from .user import _show_github, _show_wallets
from croco_cli.utils import show_key_mode, sort_wallets
from croco_cli.types import Wallet, Option


@click.group(name='set')
def _set():
    """Change settings or user details for accounts"""


def _make_wallet_option(wallet: Wallet) -> Option:
    """Create a new wallet option for keyboard interactive mode"""
    label = wallet['label']

    def _handler():
        database.set_wallet(wallet['private_key'], label)

    def _delete_handler():
        database.delete_wallet(wallet['private_key'])

    if wallet["current"]:
        label = f'{label} (Current)'

    option = Option(
        name=label,
        description=wallet['public_key'],
        handler=_handler,
        deleting_handler=_delete_handler
    )

    return option


def _show_wallet_screen() -> None:
    """Show wallet selection screen"""
    wallets = database.get_wallets()
    wallets = sort_wallets(wallets)

    options = [_make_wallet_option(wallet) for wallet in wallets]
    show_key_mode(options, 'Change wallet for unit tests', True)


@_set.command()
@click.argument('private_key', default=None, required=False)
@click.argument('label', default=None, required=False)
def wallet(private_key: str, label: Optional[str] = None) -> None:
    """Change wallet for unit tests using its private key"""
    if not private_key:
        if database.wallets.table_exists():
            _show_wallet_screen()
            return
        else:
            private_key = click.prompt('Please enter the private key of new account', hide_input=True)

    database.set_wallet(private_key, label)
    _show_wallets()


@_set.command()
@click.argument('access_token', default=None, required=False)
def git(access_token: str):
    """Change GitHub user account, using access token"""
    if not access_token:
        access_token = click.prompt('Please enter the access token of new account', hide_input=True)

    database.set_github(access_token)
    _show_github()    
