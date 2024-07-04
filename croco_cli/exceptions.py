"""
This module contains exceptions used by the croco-cli
"""


class PoetryNotFoundException(OSError):
    """Raised when poetry is not installed"""

    def __init__(self) -> None:
        super().__init__(
            'To run this command you have to install poetry. Run "pip install poetry" or "pipx install poetry"'
        )


class InvalidToken(ValueError):
    """Raised when GitHub access token is invalid"""

    def __init__(self) -> None:
        super().__init__(
            'Invalid GitHub access token. Maybe you forgot enable permission of getting email or downloading some of '
            'private repositories'
        )


class InvalidMnemonic(ValueError):
    """Raised when mnemonic of a wallet is invalid"""

    def __init__(self) -> None:
        super().__init__('Invalid mnemonic. Mnemonic must be related to the private key')