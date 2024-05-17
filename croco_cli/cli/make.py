import json
import click
from croco_cli.utils import require_wallet, constant_case
from croco_cli.database import database


@click.group()
def make():
    """Make some files for project"""


@make.command()
@require_wallet
def dotenv():
    """Make file with environment variables. Use with python-dotenv"""
    wallets = database.get_wallets()
    custom_accounts = database.get_custom_accounts(current=True)
    env_variables = database.get_env_variables()

    with open('.env', 'w') as file:
        if wallets:
            current_wallet = next(filter(lambda wallet: wallet['current'], wallets))
            file.write('# Wallet credential\n')
            file.write(f"TEST_PRIVATE_KEY='{current_wallet['private_key']}'\n")
            file.write(f"TEST_MNEMONIC='{current_wallet['mnemonic']}'\n")
            file.write("\n")

        if env_variables:
            file.write('# Environment variables\n')
            for env_var in env_variables:
                file.write(f"{env_var['key']}='{env_var['value']}'\n")
            file.write("\n")

        if custom_accounts:
            file.write('# Custom account credentials\n')
            for custom_account in custom_accounts:
                account = custom_account.pop('account')
                custom_account.pop('current')
                custom_data = json.loads(custom_account.pop('data'))
                for key, value in custom_account.items():
                    key = constant_case(f'{account}_{key}')
                    file.write(f"{key}='{value}'\n")

                for key, value in custom_data.items():
                    key = constant_case(f'{account}_{key}')
                    file.write(f"{key}='{value}'\n")

                file.write('\n')
