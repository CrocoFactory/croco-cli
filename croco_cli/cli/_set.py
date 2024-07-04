import click
from typing import Optional
from croco_cli.types import CustomAccount, Wallet
from croco_cli.utils import constant_case, catch_github_errors, catch_wallet_errors
from croco_cli._database import Database
from croco_cli.croco_echo import CrocoEcho


@click.group(name='set')
def _set():
    """Change settings or user details for accounts"""


@_set.command()
@click.argument('private_key', default=None, type=click.STRING)
@click.argument('label', default=None, required=False, type=click.STRING)
@click.argument('mnemonic', default=None, required=False, type=click.STRING)
@catch_wallet_errors
def wallet(private_key: str, label: Optional[str] = None, mnemonic: Optional[str] = None) -> None:
    """Set wallet for unit tests using its private key"""
    database = Database()

    database.set_wallet(private_key, label, mnemonic)

    public_key = database.get_public_key(private_key)
    current_wallet = Wallet(
        private_key=private_key,
        public_key=public_key,
        mnemonic=mnemonic,
        current=True,
        label=label
    )
    CrocoEcho.wallet(current_wallet)


@_set.command()
@click.argument('access_token', default=None, required=False, type=click.STRING)
@catch_github_errors
def git(access_token: str):
    """Set GitHub user account, using access token"""
    database = Database()

    if not access_token:
        access_token = click.prompt('Please enter the access token of new account', hide_input=True)

    database.set_github_user(access_token)
    CrocoEcho.github()


@_set.command()
@click.option(
    '--keyvalue',
    '-kv',
    'fields',
    help='Set an additional user field',
    nargs=2,
    multiple=True,
    type=(click.STRING, click.STRING)
)
@click.argument('account', type=click.STRING)
@click.argument('password', type=click.STRING)
@click.argument('email', type=click.STRING)
@click.argument('email_password', type=click.STRING, required=False)
def custom(
        fields: list[tuple[str, str]],
        account: str,
        password: str,
        email: str,
        email_password: Optional[str] = None
) -> None:
    """Set a custom user account"""
    database = Database()

    email_password = email_password or password

    data = {key: value for key, value in fields}

    database.set_custom_account(account, password, email, email_password, data)

    custom_account = CustomAccount(
        account=account,
        password=password,
        email=email,
        current=True,
        email_password=email_password,
        data=data
    )

    CrocoEcho.custom_account(custom_account)


@_set.command()
@click.argument('key', type=click.STRING)
@click.argument('value', type=click.STRING)
def envar(key: str, value: str) -> None:
    """Set an environment variable"""
    database = Database()

    key = constant_case(key)
    database.set_envar(key, value)
    CrocoEcho.detail(key, value, 0)
