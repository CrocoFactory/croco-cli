"""
Utility functions for croco-cli
"""
import os
import re
import curses
import getpass
from typing import Any, Callable
import click
from croco_cli.types import Option, Wallet, Package, GithubPackage
from functools import partial, wraps
from croco_cli.database import database


def snake_case(s: str) -> str:
    """
    Convert a string to snake_case.
    """
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    s = re.sub(r'\W+', '_', s).lower()
    s = re.sub(r'_+', '_', s)
    return s


def is_github_package(package: Package | GithubPackage) -> bool:
    """
    Check if a package is a GitHub package
    :param package: The package to check
    :return: True if the package is a GitHub package, false otherwise
    """
    return bool(package.get('branch'))


def _show_key_mode(
        options: list[Option],
        command_description: str,
        use_delete: bool,
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
    padded_name_len = max(len(option['name']) for option in options) + 2
    padded_description_len = max(len(option['description']) for option in options) + 2

    while True:
        stdscr.addstr(0, 0, command_description, curses.color_pair(1) | curses.A_BOLD | curses.A_REVERSE)

        for i, option in enumerate(options):
            name = option["name"].ljust(padded_name_len)
            description = option["description"].ljust(padded_description_len)

            if i == current_option:
                stdscr.addstr(i + 1, 0, f"> {name} | {description}", curses.color_pair(1))
            else:
                stdscr.addstr(i + 1, 0, f"  {name} | {description}")

        key = stdscr.getch()

        last_option_idx = len(options) - 1
        if key == curses.KEY_UP:
            if current_option > 0:
                current_option -= 1
            else:
                current_option = last_option_idx
        elif key == curses.KEY_DOWN:
            if current_option < last_option_idx:
                current_option += 1
            else:
                current_option = 0
        elif key == 127 and options[current_option]['name'] != 'Exit' and use_delete:
            options[current_option]['deleting_handler']()
            options.pop(current_option)
            stdscr.clear()
            if len(options) > 1:
                current_option = max(current_option - 1, current_option + 1)
            else:
                curses.endwin()
                return
        elif key == 10:
            selected_option = options[current_option]
            stdscr.refresh()
            curses.endwin()
            return selected_option['handler']()


def show_key_mode(
        options: list[Option],
        command_description: str,
        use_delete: bool = False
) -> None:
    """
    Shows keyboard interaction mode for the given options

    :param options: list of options to display on the screen
    :param command_description: description of the command
    :param use_delete: whether to delete options and execute deleting handler when backspace key is pressed.
    :return: None
    """
    handler = partial(_show_key_mode, options, command_description, use_delete)
    curses.wrapper(handler)


def echo_warn_mark() -> None:
    """Echo warning character on the screen"""
    click.echo(click.style(' x ', bg='red'), nl=False)
    click.echo(' ', nl=False)


def require_github(func: Callable):
    """Require a GitHub API token in order to run the command """

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not database.github_user.table_exists():
            env_token = os.environ.get("GITHUB_ACCESS_TOKEN")
            if env_token:
                database.set_github_user(env_token)
            else:
                echo_warn_mark()
                token = click.prompt('GitHub access token is missing. Set it to continue', hide_input=True)
                database.set_github_user(token)

        return func(*args, **kwargs)

    return wrapper


def require_wallet(func: Callable):
    """Require a Wallet in order to run the command"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not database.wallets.table_exists():
            env_token = os.environ.get("TEST_PRIVATE_KEY")
            if env_token:
                database.set_wallet(env_token)
            else:
                echo_warn_mark()
                token = click.prompt('Wallet private key is missing. Set it to continue', hide_input=True)
                database.set_wallet(token)
        return func(*args, **kwargs)

    return wrapper


def sort_wallets(wallets: list[Wallet]) -> list[Wallet]:
    """Sort a list of wallets"""
    wallet_number = 1
    for wallet in wallets:
        label = wallet["label"]
        if not label:
            label = f'Wallet {wallet_number}'
            wallet_number += 1

        wallet['label'] = label

    def sort_by_key(item: Wallet) -> str:
        if item['current']:
            return chr(0)
        else:
            return item['label']

    wallets = sorted(wallets, key=sort_by_key)
    return wallets


def get_cache_folder() -> str:
    username = getpass.getuser()
    os_name = os.name

    if os_name == "posix":
        cache_path = f'/Users/{username}/.cache/croco_cli'
    elif os_name == "nt":
        cache_path = f'C:\\Users\\{username}\\AppData\\Local\\croco_cli'
    else:
        raise OSError(f"Unsupported Operating System {os_name}")

    try:
        os.chdir(cache_path)
    except FileNotFoundError:
        os.mkdir(cache_path)

    return cache_path
