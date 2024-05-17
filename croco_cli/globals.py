"""
Global variables used throughout the croco-cli
"""
from croco_cli.types import Package, GithubPackage

_ADSPOWER = Package(name="adspower", description="AdsPower local API")
_CROCO_SELENIUM = Package(name="croco-selenium", description="Interact with Selenium actions")
_EVM_EXTRAS = Package(name="evm-extras", description="Utilities to develop Web3-based projects")
_EVM_WALLET = Package(name="evm-wallet", description="Wrapper over web3.py operations")
_PYTEST_EVM = Package(name="pytest-evm", description="Tools to test web3-based projects")
_PYTHON_EXTRAS = Package(name="python-extras", description="Useful extras for Python")
_SELDEGEN = Package(name="seldegen", description="Utilities to develop Selenium-based projects")

_PY_OKX = GithubPackage(name="py-okx", description="OKX Exchange API", branch='main')


PYPI_PACKAGES = (
    _ADSPOWER,
    _CROCO_SELENIUM,
    _EVM_EXTRAS,
    _EVM_WALLET,
    _PYTEST_EVM,
    _PYTHON_EXTRAS,
    _SELDEGEN
)

GITHUB_PACKAGES = (
    _PY_OKX,
    _SELDEGEN
)

PACKAGE_SETS = {
    'common': {
        'packages': (_PYTHON_EXTRAS, _PY_OKX),
        'description': 'Common package set for any project'
    },
    'selenium': {
        'packages': (
            _ADSPOWER,
            _CROCO_SELENIUM,
            _SELDEGEN
        ),
        'description': 'Package set to develop selenium based projects'
    },
    'web3': {
        'packages': (_EVM_EXTRAS, _EVM_WALLET, _PYTEST_EVM),
        'description': 'Package set to develop web3.py based projects'
    }
}
