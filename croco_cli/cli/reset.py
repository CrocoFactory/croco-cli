import click
from croco_cli.database import database


@click.command()
@click.option(
    '-u',
    '--user',
    help='Reset all user data',
    show_default=True,
    is_flag=True,
    default=True
)
@click.option(
    '-g',
    '--git',
    help='Reset GitHub user data',
    show_default=True,
    is_flag=True,
    default=False
)
@click.option(
    '-w',
    '--wallets',
    help='Reset wallet user data',
    show_default=True,
    is_flag=True,
    default=False
)
@click.option(
    '-c',
    '--custom',
    help='Reset custom user accounts',
    show_default=True,
    is_flag=True,
    default=False
)
@click.option(
    '-e',
    '--envar',
    help='Reset environment variables accounts',
    show_default=True,
    is_flag=True,
    default=False
)
def reset(user: bool, git: bool, wallets: bool, custom: bool, envar: bool):
    """Reset user accounts"""
    if git or wallets or custom or envar:
        if git:
            database.github_users.drop_table()
        if wallets:
            database.wallets.drop_table()
        if custom:
            database.custom_accounts.drop_table()
        if envar:
            database.env_variables.drop_table()
        return
    elif user:
        database.drop_database()
