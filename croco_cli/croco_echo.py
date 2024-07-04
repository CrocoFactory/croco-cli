from typing import Optional
from ._database import Database
from .tools.echo import Echo
from .types import Wallet, CustomAccount, EnvVar
from croco_cli.utils import hide_value, require_wallet, sort_wallets, require_github


class CrocoEcho(Echo):
    @classmethod
    def wallet(cls, wallet: Wallet) -> None:
        """
        Echo details of a wallet on the screen.

        :param wallet: The wallet to display.
        :return: None
        """
        label = wallet['label'] if wallet['label'] else 'Wallet'
        label = f'{label} (Current)' if wallet["current"] else label

        private_key = hide_value(wallet["private_key"], 5, 5)
        Echo.label(f'{label}')
        cls.detail('Public Key', wallet['public_key'])
        cls.detail('Private Key', private_key)
        if mnemonic := wallet.get('mnemonic'):
            first_word_len = len(mnemonic.split()[0])
            last_word_len = len(mnemonic.split()[-1])
            cls.detail('Mnemonic', hide_value(mnemonic, first_word_len, last_word_len))

    @classmethod
    @require_wallet
    def wallets(cls) -> None:
        """
        Echo wallets of the user.
        Retrieves the wallets from the database, sorts them, and displays details for each wallet on the screen.

        :return: None
        """
        database = Database()

        wallets = database.get_wallets()
        wallets = sort_wallets(wallets)
        for wallet in wallets:
            cls.wallet(wallet)

    @classmethod
    def account_dict(cls, __dict: dict[str, str], label: Optional[str] = None) -> None:
        """
        Echo an account represented as a dictionary on the screen.

        :param __dict: The dictionary representing the account.
        :param label: Optional label to display.
        :return: None
        """
        label and cls.label(f'{label}')
        for key, value in __dict.items():
            if 'password' in key or 'cookie' in key:
                continue

            if 'token'.lower() in key.lower() or 'secret' in key.lower() or 'private' in key.lower():
                value = hide_value(value, len(value) // 5, len(value) // 5)

            key = ' '.join([word.capitalize() for word in key.replace("_", " ").split()])
            cls.detail(f'{key}', value)

    @classmethod
    @require_github
    def github(cls) -> None:
        """Echo GitHub user account"""
        database = Database()

        github_user = database.get_github_user()

        if not github_user:
            cls.error('There is no GitHub to show')
            return

        access_token = hide_value(github_user['access_token'], 10)
        CrocoEcho.label('GitHub')
        CrocoEcho.detail('Login', github_user["login"])
        CrocoEcho.detail('Email', github_user["email"])
        CrocoEcho.detail('Access token', access_token)

    @classmethod
    def custom_account(cls, custom_account: CustomAccount) -> None:
        """Echo custom accounts of user"""
        custom_data = custom_account.pop('data')
        current = custom_account.pop('current')

        label = f'{custom_account.pop("account").capitalize()} (Current)' if current else custom_account.pop(
            'account').capitalize()
        cls.account_dict(custom_account, label)

        custom_data and cls.account_dict(custom_data)

    @classmethod
    def custom_accounts(cls) -> None:
        """Echo custom accounts of user. Retrieves the accounts from the database"""
        database = Database()

        custom_accounts = database.get_custom_accounts()
        if not custom_accounts:
            cls.error('There are no custom accounts to show')
            return

        for custom_account in custom_accounts:
            cls.custom_account(custom_account)

    @classmethod
    def envar(cls, envar: EnvVar) -> None:
        """Echo an environment variable."""
        CrocoEcho.detail(envar['key'], envar['value'], 0)

    @classmethod
    def envars(cls) -> None:
        database = Database()

        envars = database.get_env_variables()
        if not envars:
            cls.error('There are no environment variables to show')
            return

        for envar in envars:
            cls.envar(envar)
