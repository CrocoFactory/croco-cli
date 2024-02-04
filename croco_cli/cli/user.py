import click
from typing import Optional
from croco_cli.globals import DATABASE


@click.group()
def user():
    """Manage user accounts"""


@user.command()
@click.option(
    '--token',
    help='A personal access token for authentication on GitHub',
    type=str,
    default=None
)
def github(token: Optional[str] = None) -> None:
    """
    Authenticate with GitHub using the provided token or show current user details
    """
    click.echo()
    if token:
        DATABASE.set_github_user(token)
        click.echo('[New user]')
    else:
        click.echo('[User]')

    github_user = DATABASE.get_github_user()
    click.echo(f'   Login: {github_user["login"]}')
    click.echo(f'   Email: {github_user["email"]}')
    click.echo(f'   Access token: {github_user["access_token"]}')