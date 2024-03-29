"""
Utility functions for croco-cli
"""
import os
import re
import curses
import getpass
from typing import Any, Callable, Optional
import click
from croco_cli.types import Option, Wallet, Package, GithubPackage, AnyCallable
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


def constant_case(s: str) -> str:
    """
    Convert a string to CONSTANT_CASE.
    """
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    s = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s)
    s = re.sub(r'\W+', '_', s)
    return s.upper()


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
        stdscr: curses.window
) -> Any:
    """
    Shouldn't be used directly, instead use show_key_mode
    """

    # TODO: Sometimes, there are many options to show them instantly. Fix that

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
    padded_name_len = max([len(option['name']) for option in options]) + 2

    use_description = True
    padded_description_lengths = []
    for option in options:
        description = option.get('description', [])
        padded_description_lengths.append(len(option.get('description', [])))
        if not description:
            use_description = False
            break

    if use_description:
        padded_description_len = max(padded_description_lengths) + 2

    while True:
        stdscr.addstr(0, 0, command_description, curses.color_pair(1) | curses.A_BOLD | curses.A_REVERSE)

        for i, option in enumerate(options):
            name = option["name"].ljust(padded_name_len)

            if use_description:
                description = option['description'].ljust(padded_description_len)
                option_text = f'{name} | {description}'
            else:
                option_text = name
            if i == current_option:
                stdscr.addstr(i + 2, 0, f"> {option_text}", curses.color_pair(1))
            else:
                stdscr.addstr(i + 2, 0, f"  {option_text}")

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
        elif key == 127 and (deleting_handler := options[current_option].get('deleting_handler')):
            deleting_handler()
            options.pop(current_option)
            stdscr.clear()
            if len(options) > 1:
                if current_option > 0:
                    current_option -= 1
                else:
                    current_option += 1
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
) -> None:
    """
    Shows keyboard interaction mode for the given options

    :param options: list of options to display on the screen
    :param command_description: description of the command
    :return: None
    """
    handler = partial(_show_key_mode, options, command_description)
    curses.wrapper(handler)


def echo_error(text: str) -> None:
    """
    Echo error on the screen.

    :param text: The error message to display.
    :return: None
    """
    click.echo(click.style(' x ', bg='red'), nl=False)
    click.echo(' ', nl=False)
    click.echo(click.style(text, fg='red'))


def echo_warning(text: str) -> None:
    """
    Echo warning on the screen.

    :param text: The warning message to display.
    :return: None
    """
    click.echo(click.style(' ! ', bg='yellow'), nl=False)
    click.echo(' ', nl=False)
    click.echo(click.style(text, fg='yellow'))


def require_github(func: Callable):
    """
    Decorator to require a GitHub API token in order to run the command.

    :param func: The function to be decorated.
    :return: The decorated function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not database.github_users.table_exists():
            env_token = os.environ.get("GITHUB_ACCESS_TOKEN")
            if env_token:
                database.set_github_user(env_token)
            else:
                echo_warning('GitHub access token is missing. Set it to continue')
                token = click.prompt('', hide_input=True)
                database.set_github_user(token)

        return func(*args, **kwargs)

    return wrapper


def require_wallet(func: Callable):
    """
    Decorator to require a Wallet in order to run the command.

    :param func: The function to be decorated.
    :return: The decorated function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not database.wallets.table_exists():
            env_token = os.environ.get("TEST_PRIVATE_KEY")
            if env_token:
                database.set_wallet(env_token)
                return func(*args, **kwargs)
            else:
                echo_warning('Wallet private key is missing. Set it to continue (croco set wallet).')
        else:
            return func(*args, **kwargs)
    return wrapper


def sort_wallets(wallets: list[Wallet]) -> list[Wallet]:
    """
    Sort a list of wallets.

    :param wallets: List of wallets to be sorted.
    :return: Sorted list of wallets.
    """
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
    """
    Get the cache folder path based on the operating system.

    :return: Cache folder path.
    """
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


def show_label(label: str, padding: Optional[int] = 0) -> None:
    """
    Echo label on the screen.

    :param label: The label to display.
    :param padding: Optional padding for indentation.
    :return: None
    """
    padding = '     ' * padding
    click.echo(click.style(f'{padding}[{label}]', fg='blue', bold=True))


def show_detail(key: str, value: str, padding: Optional[int] = 1) -> None:
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


def hide_value(value: str, begin_part: int, end_part: int = 8) -> str:
    """
    Hide part of the value, replacing it with *.

    :param value: The original value.
    :param begin_part: The number of characters to show at the beginning.
    :param end_part: The number of characters to show at the end.
    :return: The modified value with hidden parts.
    """
    value = value[:begin_part] + '****...' + value[-end_part:]
    return value


def show_account_dict(__dict: dict[str, str], label: Optional[str] = None) -> None:
    """
    Echo an account represented as a dictionary on the screen.

    :param __dict: The dictionary representing the account.
    :param label: Optional label to display.
    :return: None
    """
    label and show_label(f'{label}')
    for key, value in __dict.items():
        if 'password' in key or 'cookie' in key:
            continue

        if 'token'.lower() in key.lower() or 'secret' in key.lower() or 'private' in key.lower():
            value = hide_value(value, len(value) // 5, len(value) // 5)

        key = ' '.join([word.capitalize() for word in key.replace("_", " ").split()])
        show_detail(f'{key}', value)


def make_screen_option(
        label: str,
        description: Optional[str],
        options: list[Option],
        deleting_handler: Optional[AnyCallable] = None
) -> Option:
    """
    Returns an option navigating to a new screen.

    :param label: The label for the option.
    :param description: The description for the option.
    :param options: List of options for the new screen.
    :param deleting_handler: Optional handler for deleting the option.
    :return: The created Option instance.
    """
    def _handler():
        show_key_mode(options, description)

    option = Option(
        name=label,
        handler=_handler,
        deleting_handler=deleting_handler
    )

    return option


def get_back_option(
        options: list[Option]
):
    """
    Returns an option navigating to the previous screen.

    :param options: List of options for the previous screen.
    :return: The created Option instance for going back.
    """
    return make_screen_option('Back', f'Return to the previous screen', options)


def show_wallet(wallet: Wallet) -> None:
    """
    Echo details of a wallet on the screen.

    :param wallet: The wallet to display.
    :return: None
    """
    label = f'{wallet["label"]} (Current)' if wallet["current"] else wallet['label']

    private_key = hide_value(wallet["private_key"], 5, 5)
    show_label(f'{label}')
    show_detail('Public Key', wallet['public_key'])
    show_detail('Private Key', private_key)
    if mnemonic := wallet.get('mnemonic'):
        first_word_len = len(mnemonic.split()[0])
        last_word_len = len(mnemonic.split()[-1])
        show_detail('Mnemonic', hide_value(mnemonic, first_word_len, last_word_len))


@require_wallet
def show_wallets() -> None:
    """
    Echo wallets of the user.
    Retrieves the wallets from the database, sorts them, and displays details for each wallet on the screen.

    :return: None
    """
    wallets = database.get_wallets()
    wallets = sort_wallets(wallets)
    for wallet in wallets:
        show_wallet(wallet)
