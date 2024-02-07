import click
from croco_cli.utils import require_wallet
from croco_cli.database import database


@click.group()
def make():
    """Make some files for project"""


@make.command()
@require_wallet
def dotenv():
    """Make file with environment variables. Use with python-dotenv"""
    wallets = database.get_wallets()
    current_wallet = next(filter(lambda wallet: wallet['current'], wallets))

    with open('.env', 'w') as file:
        file.write(f"TEST_PRIVATE_KEY={current_wallet['private_key']}")
