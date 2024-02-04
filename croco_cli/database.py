"""
This module provides a database interface
"""

import os
import pickle
from github import Auth
from github import Github
from typing import ClassVar, Type
from croco_cli.types import GithubUser
from peewee import Model, CharField, BlobField, SqliteDatabase

_CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


class Database:
    _path: ClassVar[str] = os.path.join(_CURRENT_PATH, 'user.db')
    _database: ClassVar[SqliteDatabase] = SqliteDatabase(_path)

    def __init__(self):
        self.path = self._path

        class GithubUserModel(Model):
            data = BlobField()
            login = CharField(unique=True)
            name = CharField()
            email = CharField(unique=True)
            access_token = CharField(unique=True)

            class Meta:
                database = Database._database
                table_name = 'github_users'

        self._github_user_table = GithubUserModel
        self._build_database()

    @property
    def github_user_table(self) -> Type[Model]:
        """
        :return: the database model for the GitHub user table
        """
        return self._github_user_table

    def get_github_user(self) -> GithubUser:
        """
        Returns the info about the GitHub user
        :return: The info about the GitHub user represented as GithubUser dictionary
        """
        query = self.github_user_table.select()

        for user in query:
            return GithubUser(
                data=pickle.loads(user.data),
                login=user.login,
                name=user.name,
                email=user.email,
                access_token=user.access_token
            )

    def _build_github_user(self) -> None:
        github_user = self._github_user_table
        database = self._database

        if not github_user.table_exists():
            token = os.environ.get('GITHUB_API_TOKEN')
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

    def _build_database(self):
        self._build_github_user()
