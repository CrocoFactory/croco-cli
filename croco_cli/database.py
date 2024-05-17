"""
This module provides a database interface
"""
import json
import os
import pickle
import getpass
from eth_account import Account
from github import Auth
from github import Github
from typing import Type, Optional, ClassVar
from croco_cli.types import GithubUser, Wallet, CustomAccount, EnvVariable
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
            mnemonic = CharField(unique=True, null=True)
            current = BooleanField()
            label = CharField(null=True)

            class Meta:
                database = Database.interface
                table_name = 'wallets'

        class CustomAccountModel(Model):
            account = CharField()
            password = CharField()
            email = CharField()
            email_password = CharField()
            current = BooleanField()
            data = CharField(null=True)

            class Meta:
                database = Database.interface
                table_name = 'custom_accounts'

        class EnvVariableModel(Model):
            key = CharField(unique=True)
            value = CharField()

            class Meta:
                database = Database.interface
                table_name = 'env_variables'

        self._github_users = GithubUserModel
        self._wallets = WalletModel
        self._custom_accounts = CustomAccountModel
        self._env_variables = EnvVariableModel

    @property
    def github_users(self) -> Type[Model]:
        """
        :return: the database model for the GitHub user table
        """
        return self._github_users

    @property
    def wallets(self) -> Type[Model]:
        """
        :return: the database model for the wallet table
        """
        return self._wallets

    @property
    def custom_accounts(self) -> Type[Model]:
        """
        :return: the database model for the custom Account table
        """
        return self._custom_accounts

    @property
    def env_variables(self) -> Type[Model]:
        """
        :return: the database model for the environment variable table
        """
        return self._env_variables

    def drop_database(self) -> None:
        """
        Drops the database
        :return: None
        """
        self.interface.drop_tables([self.github_users, self.wallets, self.custom_accounts, self.env_variables])

    def get_wallets(self) -> list[Wallet] | None:
        """
        Returns a list of all ethereum wallets of the user
        :return: a list of all ethereum wallets of the user
        """
        query = self.wallets.select()
        if not self.wallets.table_exists():
            return None

        wallets = [
            Wallet(
                public_key=wallet.public_key,
                private_key=wallet.private_key,
                mnemonic=wallet.mnemonic,
                current=wallet.current,
                label=wallet.label
            )
            for wallet in query
        ]
        return wallets

    def get_github_user(self) -> GithubUser | None:
        """
        Returns the info about the GitHub user
        :return: The info about the GitHub user represented as GithubUser dictionary
        """
        query = self.github_users.select()
        if not self.github_users.table_exists():
            return None

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
        github_users = self._github_users
        self.interface.create_tables([github_users])

        if github_users.table_exists():
            github_users.delete().execute()

        _auth = Auth.Token(token)

        with Github(auth=_auth) as github_api:
            user = github_api.get_user()
            _emails = user.get_emails()

            for email in _emails:
                if email.primary:
                    user_email = email.email
                    break

        github_users.create(
            data=pickle.dumps(user),
            login=user.login,
            name=user.name,
            email=user_email,
            access_token=token
        )

    def delete_github_user(self, token: str) -> None:
        github_user = self._github_users
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

    def set_wallet(
            self,
            private_key: str,
            label: Optional[str] = None,
            mnemonic: Optional[str] = None
    ) -> None:
        """
        Sets the wallet using a private key and a label
        :param private_key: Private key of the wallet
        :param label: Label for the wallet
        :param mnemonic: mnemonic of a wallet
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
                mnemonic=mnemonic,
                current=True,
                label=label
            )

    def get_custom_accounts(
            self,
            account: Optional[str] = None,
            current: bool = False
    ) -> list[CustomAccount] | None:
        """
        Returns list of custom accounts of user
        :param account: A name of accounts
        :param current: Whether accounts should be current
        :return:
        """
        custom_accounts = self._custom_accounts

        if not custom_accounts.table_exists():
            return

        if account:
            query = custom_accounts.select().where(custom_accounts.account == account)
        else:
            query = self.custom_accounts.select()

        if current:
            query = filter(lambda current_account: current_account.current, query)

        accounts = [
            CustomAccount(
                account=account.account,
                password=account.password,
                current=account.current,
                email=account.email,
                email_password=account.email_password,
                data=account.data
            )
            for account in query
        ]
        return accounts

    def set_custom_account(
            self,
            account: str,
            password: str,
            email: str,
            email_password: Optional[str] = None,
            data: Optional[dict[str, str]] = None
    ) -> None:
        """
        Sets a custom user account
        :param account: A name of account
        :param password: Password
        :param email: Email login
        :param email_password: Email password. If not provided, the password will be used as the password for the account
        :param data: Custom user data
        :return: None
        """
        custom_accounts = self._custom_accounts
        database = self.interface

        database.create_tables([custom_accounts])

        existing_accounts = custom_accounts.select().where(custom_accounts.account == account)

        skip_creating = False
        if len(existing_accounts) > 0:
            for existing_account in existing_accounts:
                if existing_account.email == email:
                    existing_account.current = True
                    existing_account.save()
                    skip_creating = True
                    continue

                if existing_account.current:
                    existing_account.current = False
                    existing_account.save()

        if not skip_creating:
            custom_accounts.create(
                account=account,
                password=password,
                current=True,
                email=email,
                email_password=email_password,
                data=json.dumps(data)
            )

    def delete_custom_accounts(self, account: str, email: str) -> None:
        """
        Delete custom user accounts
        :param account: A name of accounts
        :param email: Email of accounts
        :return: None
        """
        custom_accounts = self._custom_accounts
        custom_accounts.delete().where(
            custom_accounts.account == account and custom_accounts.email == email
        ).execute()

    def set_env_variable(
            self,
            key: str,
            value: str
    ) -> None:
        env_variables = self._env_variables
        self.interface.create_tables([env_variables])

        existing_variables = env_variables.select().where(env_variables.key == key)
        if len(existing_variables):
            for existing_variable in existing_variables:
                existing_variable.value = value
                break
        else:
            env_variables.create(
                key=key,
                value=value
            )

    def get_env_variables(self) -> list[EnvVariable] | None:
        env_variables = self._env_variables
        if not env_variables.table_exists():
            return 

        query = env_variables.select()

        return [
            EnvVariable(
                key=env_variable.key,
                value=env_variable.value
            )
            for env_variable in query
        ]

    def delete_env_variables(self) -> None:
        env_variables = self._env_variables
        env_variables.delete().execute()


database = Database()
