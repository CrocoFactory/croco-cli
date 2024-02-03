"""
Global variables used throughout the croco-cli
"""

import os
from croco_cli.types import Package, GithubPackage
from github import Github
from github import Auth

PYPI_PACKAGES = (
    Package(name="adspower", description="AdsPower local API"),
    Package(name="croco-selenium", description="Interact with Selenium Web Driver actions"),
    Package(name="evm-extras", description="Utilities to develop Web3-based projects"),
    Package(name="evm-wallet", description="Wrapper over web3.py operations"),
    Package(name="pytest-evm", description="Tools to test web3-based projects"),
    Package(name="python-extras", description="Useful extras for Python")
)

GITHUB_PACKAGES = (
    GithubPackage(name="py-okx", description="OKX Exchange API", branch='main'),
    GithubPackage(name="seldegen", description="Utilities to develop Selenium-based projects", branch='test')
)

GITHUB_API_TOKEN = os.environ.get('GITHUB_API_TOKEN')

_auth = Auth.Token(GITHUB_API_TOKEN)

with Github(auth=_auth) as github_api:
    GITHUB_USER = github_api.get_user()
    GITHUB_USER_LOGIN = GITHUB_USER.login
    GITHUB_USER_NAME = GITHUB_USER.name
    _emails = GITHUB_USER.get_emails()

    for email in _emails:
        if email.primary:
            GITHUB_USER_EMAIL = email.email
            break
