"""
Global variables used throughout the croco-cli
"""

from croco_cli.types import Package, GithubPackage
from .database import Database

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

DATABASE = Database()

_github_user = DATABASE.get_github_user()
GITHUB_USER_EMAIL = _github_user['email']
GITHUB_USER_LOGIN = _github_user['login']
GITHUB_USER_NAME = _github_user['name']
GITHUB_USER_DATA = _github_user['data']
GITHUB_API_TOKEN = _github_user['access_token']
