import click
from typing import Optional
from croco_cli.database import database
from croco_cli.types import CustomAccount, Wallet
from .user import _show_github, _show_custom_account
from croco_cli.utils import show_wallet, show_detail, constant_case


@click.group(name='set')
def _set():
    """Change settings or user details for accounts"""


@_set.command()
@click.argument('private_key', default=None, type=click.STRING)
@click.argument('label', default=None, required=False, type=click.STRING)
@click.argument('mnemonic', default=None, required=False, type=click.STRING)
def wallet(private_key: str, label: Optional[str] = None, mnemonic: Optional[str] = None) -> None:
    """Set wallet for unit tests using its private key"""
    database.set_wallet(private_key, label, mnemonic)
    public_key = database.get_public_key(private_key)
    current_wallet = Wallet(
        private_key=private_key,
        public_key=public_key,
        mnemonic=mnemonic,
        current=True,
        label=label
    )
    show_wallet(current_wallet)


@_set.command()
@click.argument('access_token', default=None, required=False, type=click.STRING)
def git(access_token: str):
    """Set GitHub user account, using access token"""
    if not access_token:
        access_token = click.prompt('Please enter the access token of new account', hide_input=True)

    database.set_github(access_token)
    _show_github()


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

    _show_custom_account(custom_account)


@_set.command()
@click.argument('key', type=click.STRING)
@click.argument('value', type=click.STRING)
def envar(key: str, value: str) -> None:
    """Set an environment variable"""
    key = constant_case(key)
    database.set_env_variable(key, value)
    show_detail(key, value, 0)
