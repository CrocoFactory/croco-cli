import click
from croco_cli._database import Database
from croco_cli.tools.keymode import KeyMode
from croco_cli.tools.option import Option
from croco_cli.types import CustomAccount
from croco_cli.utils import Wallet
from croco_cli.utils import sort_wallets
from croco_cli.croco_echo import CrocoEcho


@click.group()
def change():
    """Change current user accounts"""


def _make_wallet_option(wallet: Wallet) -> Option:
    """Create a new wallet option for keyboard interactive mode"""
    label = wallet['label']
    database = Database()

    def _handler():
        database.set_wallet(wallet['private_key'], label)

    def _deleting_handler():
        database.delete_wallet(wallet['private_key'])
        wallets = database.get_wallets()

        if wallets:
            try:
                last_wallet = database.get_wallets()[-1]
                current_wallet = filter(lambda x: x['current'], wallets)

                try:
                    current_wallet = next(current_wallet)
                except StopIteration:
                    current_wallet = None

                if not current_wallet:
                    database.set_wallet(
                        last_wallet['private_key'],
                        last_wallet['label'],
                        last_wallet['mnemonic']
                    )
            except IndexError:
                pass

    if wallet["current"]:
        label = f'{label} (Current)'

    option = Option(
        name=label,
        description=wallet['public_key'],
        handler=_handler,
        deleting_handler=_deleting_handler
    )

    return option


def _make_custom_option(account: CustomAccount) -> Option:
    """Create a new custom account option for keyboard interactive mode"""
    label = account["email"]
    database = Database()

    def _handler():
        account.pop('current')
        database.set_custom_account(**account)

    def _deleting_handler():
        database.delete_custom_accounts(account['account'], account['email'])

        custom_accounts = database.get_custom_accounts(account['account'])

        if custom_accounts:
            try:
                last_custom_account = custom_accounts[-1]
                current_account = filter(lambda x: x['current'], custom_accounts)

                try:
                    current_account = next(current_account)
                except StopIteration:
                    current_account = None

                if not current_account:
                    last_custom_account.pop('current')
                    database.set_custom_account(**last_custom_account)
            except IndexError:
                pass

    if account["current"]:
        label = f'{label} (Current)'

    option = Option(
        name=label,
        handler=_handler,
        deleting_handler=_deleting_handler
    )

    return option


@change.command(name='wallet')
def _wallet():
    """Change the current wallet for unit tests"""
    wallets = []
    database = Database()

    if database.wallets.table_exists():
        wallets = database.get_wallets()

    if len(wallets) < 2:
        CrocoEcho.error('There are no wallets in the database to change.')
        return

    wallets = sort_wallets(wallets)

    options = [_make_wallet_option(wallet) for wallet in wallets]
    keymode = KeyMode(options, 'Change wallet for unit tests')
    keymode()


@change.command()
def custom():
    """Change the custom user account"""
    accounts_map = dict()
    database = Database()

    custom_accounts = database.get_custom_accounts()
    if not custom_accounts or not len(custom_accounts):
        CrocoEcho.error('There are no custom accounts in the database to change.')
        return

    for account in custom_accounts:
        accounts = accounts_map.get(account['account'])
        if isinstance(accounts, list):
            accounts_map[account['account']].append(account)
        else:
            accounts_map[account['account']] = [account]

    screen_options = []
    for key, value in accounts_map.items():
        if len(value) < 2:
            continue

        account_options = [_make_custom_option(account) for account in value]
        description = f'Change {key.capitalize()} account'

        def deleting_handler():
            database.delete_custom_accounts(key)

        screen_options.append(
            KeyMode.screen_option(
                key.capitalize(),
                description,
                account_options,
                deleting_handler
            )
        )

    if not len(screen_options):
        CrocoEcho.error('There are no custom accounts in the database to change.')
        return

    keymode = KeyMode(screen_options, 'Change custom account')
    keymode()
