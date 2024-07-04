import click
from croco_cli.croco_echo import CrocoEcho


@click.command()
@click.option(
    '--git',
    '-g',
    'info',
    help='Show GitHub user account',
    flag_value='git',
    default=True
)
@click.option(
    '--wallets',
    '-w',
    'info',
    help='Show wallets of user',
    flag_value='wallets',
    default=False
)
@click.option(
    '--custom',
    '-c',
    'info',
    help='Show custom accounts of user',
    flag_value='custom',
    default=False
)
@click.option(
    '--env',
    '-e',
    'info',
    help='Show environment variables of user',
    flag_value='env',
    default=False
)
def user(info: str) -> None:
    """Show user accounts"""
    match info:
        case 'wallets':
            CrocoEcho.wallets()
        case 'custom':
            CrocoEcho.custom_accounts()
        case 'git':
            CrocoEcho.github()
        case 'env':
            CrocoEcho.envars()
