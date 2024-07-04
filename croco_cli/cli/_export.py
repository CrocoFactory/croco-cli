"""
This module contains functions to export cli settings and accounts
"""
import click
import json
from croco_cli._database import Database
from typing import Optional
from croco_cli.croco_echo import CrocoEcho


@click.command()
@click.option('-i', '--indent', 'indent', is_flag=True, default=False, show_default=True, help='Export using indentations')
@click.argument('path', default=None, type=click.Path(file_okay=True), required=False)
def export(path: Optional[str] = None, indent: bool = True) -> None:
    """Export cli configuration"""
    path = 'croco_config.json' if not path else path
    database = Database()

    env_vars = database.get_env_variables()
    wallets = database.get_wallets()
    github_user = database.get_github_user()
    custom_accounts = database.get_custom_accounts()

    if env_vars:
        env_vars = {var['key']: var['value'] for var in env_vars}

    config = {
        'user': {
            'wallets': [wallet.pop('public_key') and wallet for wallet in wallets] if wallets else None,
            'custom': custom_accounts if custom_accounts else None,
            'github': github_user['access_token'] if github_user else None,
            'env': env_vars if env_vars else None
        }
    }

    try:
        with open(path, 'w') as file:
            indent = 2 if indent else None
            json.dump(config, file, indent=indent)
    except (FileNotFoundError, NotADirectoryError):
        CrocoEcho.error('All folders in path must exist')
