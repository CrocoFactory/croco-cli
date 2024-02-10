"""
This module provides a database interface
"""
import os
import pickle
import getpass
from eth_account import Account
from github import Auth
from github import Github
from typing import Type, Optional, ClassVar
from croco_cli.types import GithubUser, Wallet
from peewee import Model, CharField, BlobField, SqliteDatabase, BooleanField


def _get_cache_folder() -> str:
    username = getpass.getuser()
    os_name = os.name

    if os_name == "posix":
        cache_path = f'/Users/{username}/.cache/croco_cli'
    elif os_name == "nt":
        cache_path = f'C:\\Users\\{username}\\AppData\\Local\\croco_cli'
    else:
        raise OSError(f"Unsupported Operating System {os_name}")

    try:
        os.mkdir(cache_path)
    except FileExistsError:
        pass

    return cache_path


class Database:
    _path: ClassVar[str] = os.path.join(_get_cache_folder(), 'user.db')
    interface: ClassVar[SqliteDatabase] = SqliteDatabase(_path)

    def __init__(self):
        class GithubUserModel(Model):
            data = BlobField()
            login = CharField(unique=True)
            name = CharField()
            email = CharField(unique=True)
            access_token = CharField(unique=True)

            class Meta:
                database = Database.interface
                table_name = 'github_users'

        class WalletModel(Model):
            public_key = CharField(unique=True)
            private_key = CharField(unique=True)
            current = BooleanField()
            label = CharField(null=True)

            class Meta:
                database = Database.interface
                table_name = 'wallets'

        self._github_user = GithubUserModel
        self._wallets = WalletModel

    @property
    def github_user(self) -> Type[Model]:
        """
        :return: the database model for the GitHub user table
        """
        return self._github_user

    @property
    def wallets(self) -> Type[Model]:
        """
        :return: the database model for the Wallet
        """
        return self._wallets

    def get_wallets(self) -> list[Wallet]:
        """
        Returns a list of all ethereum wallets of the user
        :return: a list of all ethereum wallets of the user
        """
        query = self.wallets.select()
        wallets = [
            Wallet(
                public_key=wallet.public_key,
                private_key=wallet.private_key,
                current=wallet.current,
                label=wallet.label
            )
            for wallet in query
        ]
        return wallets

    def get_github_user(self) -> GithubUser:
        """
        Returns the info about the GitHub user
        :return: The info about the GitHub user represented as GithubUser dictionary
        """
        query = self.github_user.select()

        for user in query:
            return GithubUser(
                data=pickle.loads(user.data),
                login=user.login,
                name=user.name,
                email=user.email,
                access_token=user.access_token
            )

    def set_github_user(self, token: str) -> None:
        """
        Sets the GitHub user using a personal access token
        :param token: A personal access token
        :return: None
        """
        github_user = self._github_user
        database = self.interface

        if github_user.table_exists():
            github_user.delete().execute()

        _auth = Auth.Token(token)

        with Github(auth=_auth) as github_api:
            user = github_api.get_user()
            _emails = user.get_emails()

            for email in _emails:
                if email.primary:
                    user_email = email.email
                    break

        database.create_tables([github_user])

        github_user.create(
            data=pickle.dumps(user),
            login=user.login,
            name=user.name,
            email=user_email,
            access_token=token
        )

    def delete_github_user(self, token: str) -> None:
        github_user = self._github_user
        github_user.delete().where(github_user.access_token == token).execute()

    def delete_wallet(self, private_key: str) -> None:
        wallets_table = self._wallets
        wallets_table.delete().where(wallets_table.private_key == private_key).execute()

    @staticmethod
    def get_public_key(private_key: str) -> str:
        """
        Get public key from a private key
        :param private_key: The private key
        :return: The public key
        """
        account = Account.from_key(private_key)
        public_key = account.address
        return public_key

    def set_wallet(self, private_key: str, label: Optional[str] = None) -> None:
        """
        Sets the wallet using a private key and a label
        :param private_key: Private key of the wallet
        :param label: Label for the wallet
        :return: None
        """
        wallets = self._wallets
        database = self.interface

        database.create_tables([wallets])

        existing_wallets = wallets.select().where(wallets.private_key == private_key)

        current_wallets = wallets.select().where(wallets.current)
        if len(current_wallets) == 1:
            for current_wallet in current_wallets:
                current_wallet.current = False
                current_wallet.save()
                break

        if len(existing_wallets) == 1:
            for wallet in existing_wallets:
                wallet.current = True
                wallet.save()
                break
        else:
            public_key = self.get_public_key(private_key)
            wallets.create(
                public_key=public_key,
                private_key=private_key,
                current=True,
                label=label
            )


database = Database()
