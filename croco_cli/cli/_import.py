"""
This module contains functions to import cli settings and accounts
"""

import click
import json
from croco_cli._database import Database
from croco_cli.utils import catch_github_errors, catch_wallet_errors


@click.command(name='import')
@click.argument('path', type=click.Path(exists=True))
@catch_wallet_errors
@catch_github_errors
def _import(path: str) -> None:
    """Import cli configuration"""
    database = Database()

    with open(path, 'r') as file:
        config = json.load(file)

    user = config['user']

    if token := user['github']:
        database.set_github_user(token)

    if wallets := user['wallets']:
        current_wallet = None
        for wallet in wallets:
            if not wallet.pop('current'):
                database.set_wallet(**wallet)
            else:
                current_wallet = wallet

        database.set_wallet(**current_wallet)

    if custom_accounts := user['custom']:
        current_accounts = []
        for account in custom_accounts:
            if not account.pop('current'):
                database.set_custom_account(**account)
            else:
                current_accounts.append(account)

        for account in current_accounts:
            database.set_custom_account(**account)

    if env := user['env']:
        for key, value in env.items():
            database.set_envar(key, value)
