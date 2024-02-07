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
def reset(user: bool, git: bool, wallets: bool):
    """Reset user accounts"""
    if git or wallets:
        if git:
            database.github_user.drop_table()
        if wallets:
            database.wallets.drop_table()
        return
    elif user:
        database.interface.drop_database()
