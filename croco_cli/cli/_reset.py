import click
from croco_cli._database import Database


@click.command()
@click.option(
    '-u',
    '--user',
    'info',
    help='Reset all user data',
    show_default=True,
    flag_value='user',
    default=True
)
@click.option(
    '--git',
    '-g',
    'info',
    help='Reset GitHub user data',
    flag_value='git',
    default=True
)
@click.option(
    '--wallets',
    '-w',
    'info',
    help='Reset wallet user data',
    flag_value='wallets',
    default=False
)
@click.option(
    '--custom',
    '-c',
    'info',
    help='Reset custom user accounts',
    flag_value='custom',
    default=False
)
@click.option(
    '--env',
    '-e',
    'info',
    help='Reset environment variables accounts',
    flag_value='env',
    default=False
)
def reset(info: str):
    """Reset user accounts"""
    database = Database()

    match info:
        case 'git':
            database.github_users.drop_table()
        case 'wallets':
            database.wallets.drop_table()
        case 'custom':
            database.custom_accounts.drop_table()
        case 'envar':
            database.env_variables.drop_table()
        case 'user':
            database.drop_database()
