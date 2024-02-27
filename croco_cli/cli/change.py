import click
from croco_cli.database import database
from croco_cli.types import Option, Wallet, CustomAccount
from croco_cli.utils import show_key_mode, sort_wallets, echo_error, make_screen_option


@click.group()
def change():
    """Change current user accounts"""


def _make_wallet_option(wallet: Wallet) -> Option:
    """Create a new wallet option for keyboard interactive mode"""
    label = wallet['label']

    def _handler():
        database.set_wallet(wallet['private_key'], label)

    def _deleting_handler():
        database.delete_wallet(wallet['private_key'])

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

    def _handler():
        account.pop('current')
        database.set_custom_account(**account)

    def _deleting_handler():
        database.delete_custom_accounts(account['account'], account['email'])

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
    if database.wallets.table_exists():
        wallets = database.get_wallets()

    if len(wallets) < 2:
        echo_error('There are no wallets in the database to change.')
        return

    wallets = sort_wallets(wallets)

    options = [_make_wallet_option(wallet) for wallet in wallets]
    show_key_mode(options, 'Change wallet for unit tests')


@change.command()
def custom():
    """Change the custom user account"""
    accounts_map = dict()

    custom_accounts = database.get_custom_accounts()
    if not len(custom_accounts):
        echo_error('There are no custom accounts in the database to change.')
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
            custom_accounts = database.custom_accounts
            custom_accounts.delete().where(custom_accounts.account == key).execute()

        screen_options.append(
            make_screen_option(
                key.capitalize(),
                description,
                account_options,
                deleting_handler
            )
        )

    if not len(screen_options):
        echo_error('There are no custom accounts in the database to change.')
        return

    show_key_mode(screen_options, 'Change custom account')
