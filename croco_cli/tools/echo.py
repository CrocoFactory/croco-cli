"""
Class for echoing messages
"""
import click
from typing import Optional, Any, IO


class Echo:
    @staticmethod
    def warning(text: str) -> None:
        """
        Echo warning on the screen.

        :param text: The warning message to display.
        :return: None
        """
        click.echo(click.style(' ! ', bg='yellow'), nl=False)
        click.echo(' ', nl=False)
        click.echo(click.style(text, fg='yellow'))

    @staticmethod
    def error(text: str) -> None:
        """
        Echo error on the screen.

        :param text: The error message to display.
        :return: None
        """
        click.echo(click.style(' x ', bg='red'), nl=False, err=True)
        click.echo(' ', nl=False, err=True)
        click.echo(click.style(text, fg='red'), err=True)

    @staticmethod
    def label(label: str, padding: Optional[int] = 0) -> None:
        """
        Echo label on the screen.

        :param label: The label to display.
        :param padding: Optional padding for indentation.
        :return: None
        """
        padding = '     ' * padding
        click.echo(click.style(f'{padding}[{label}]', fg='blue', bold=True))

    @staticmethod
    def detail(key: str, value: str, padding: Optional[int] = 1) -> None:
        """
        Echo detail on the screen.

        :param key: The detail key.
        :param value: The detail value.
        :param padding: Optional padding for indentation.
        :return: None
        """
        padding = '     ' * padding
        click.echo(click.style(f'{padding}{key}: ', fg='magenta'), nl=False)
        click.echo(click.style(f'{value}', fg='green'))

    @staticmethod
    def text(
            message: Optional[Any] = None,
            file: Optional[IO[Any]] = None,
            nl: bool = True,
            err: bool = False,
            color: Optional[bool] = None
    ) -> None:
        click.echo(message, file=file, err=err, color=color, nl=nl)
        
    @staticmethod
    def stext(
        message: Optional[Any] = None,
        file: Optional[IO[bytes | str]] = None,
        nl: bool = True,
        err: bool = False,
        color: Optional[bool] = None,
        **styles: Any,
    ) -> None:
        click.secho(message, file=file, err=err, color=color, nl=nl, **styles)
