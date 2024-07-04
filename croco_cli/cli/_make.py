import click
from croco_cli._database import Database
from croco_cli.croco_echo import CrocoEcho
from croco_cli.utils import constant_case


@click.group()
def make():
    """Make some files for project"""


@make.command()
@click.argument('path', default='.env', required=False, type=click.Path(dir_okay=True))
def dotenv(path: str = '.env'):
    """Make file with environment variables. Use with python-dotenv"""
    database = Database()

    current_wallet = database.get_wallets(current=True)[0]
    custom_accounts = database.get_custom_accounts(current=True)
    env_variables = database.get_env_variables()

    try:
        with open(path, 'w') as file:
            if current_wallet:
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
                    custom_data = custom_account.pop('data')
                    for key, value in custom_account.items():
                        key = constant_case(f'{account}_{key}')
                        file.write(f"{key}='{value}'\n")

                    for key, value in custom_data.items():
                        key = constant_case(f'{account}_{key}')
                        file.write(f"{key}='{value}'\n")

                    file.write('\n')
    except (FileNotFoundError, NotADirectoryError):
        CrocoEcho.error('All folders in path must exist')
