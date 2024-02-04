"""
Utility functions for croco-cli
"""
import os
import re
import curses
from typing import Any, Callable
import click
from croco_cli.types import Option
from functools import partial, wraps
from .globals import DATABASE


def snake_case(s: str) -> str:
    """
    Convert a string to snake_case.
    """
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    s = re.sub(r'\W+', '_', s).lower()
    s = re.sub(r'_+', '_', s)
    return s


def _show_key_mode(
        options: list[Option],
        command_description: str,
        stdscr: curses.window
) -> Any:
    """
    Shouldn't be used directly, instead use show_key_mode
    """
    exit_option = Option(
        name='Exit',
        description='Return to the terminal',
        handler=curses.endwin
    )

    options.append(exit_option)

    curses.curs_set(0)  # Hide the cursor
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)  # Color pair for selected option

    stdscr.clear()
    stdscr.refresh()

    # Set up initial variables
    current_option = 0

    while True:
        stdscr.addstr(0, 0, command_description, curses.A_BOLD)

        for i, option in enumerate(options):
            name = option["name"]
            description = option["description"]

            if i == current_option:
                stdscr.addstr(i + 2, 0, f"> {name}: {description}", curses.color_pair(1) | curses.A_REVERSE)
            else:
                stdscr.addstr(i + 2, 0, f"  {name}: {description}")

        key = stdscr.getch()

        if key == curses.KEY_UP and current_option > 0:
            current_option -= 1
        elif key == curses.KEY_DOWN and current_option < len(options) - 1:
            current_option += 1
        elif key == 10:
            selected_option = options[current_option]
            stdscr.refresh()
            curses.endwin()

            return selected_option['handler']()


def show_key_mode(
        options: list[Option],
        command_description: str,
) -> None:
    """
    Shows keyboard interaction mode for the given options

    :param options: list of options to display on the screen
    :param command_description: description of the command
    :return: None
    """
    handler = partial(_show_key_mode, options, command_description)
    curses.wrapper(handler)


def require_github(func: Callable):
    """Require a GitHub API token in order to run the command """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not DATABASE.github_user.table_exists():
            env_token = os.environ.get("GITHUB_ACCESS_TOKEN")
            if env_token:
                DATABASE.set_github_user(env_token)
            else:
                token = click.prompt('GitHub access token is missing. Set it to continue', hide_input=True)
                DATABASE.set_github_user(token)

        return func(*args, **kwargs)
    return wrapper
