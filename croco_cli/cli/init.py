"""
This module contains functions to initialize python packages and projects
"""

import os
import click 
from croco_cli.utils import snake_case, require_github
from croco_cli.database import database


@click.group()
def init():
    """Initialize python packages and projects"""


def _add_poetry(
        project_name: str,
        description: str,
        is_package: bool
) -> None:
    """
    Adds a pyproject.toml file
    :param project_name: Name of the package
    :param description: The description of the project
    :param is_package: Whether project should be configured as Python package
    :return: None
    """
    snaked_name = snake_case(project_name)
    github_user = database.get_github_user()

    intended_audience = 'Intended Audience :: Customer Service' if not is_package else 'Intended Audience :: Developers'

    toml = 'pyproject.toml'
    with open(toml, 'w') as toml_file:
        toml_file.write(f"""[tool.poetry]
name = '{snaked_name}'
version = '0.1.0'
description = '{description}'
authors = ['{github_user['name']} <{github_user['email']}>']
license = 'MIT'
readme = 'README.md'
repository = 'https://github.com/{github_user['login']}/{project_name}'
homepage = 'https://github.com/{github_user['login']}/{project_name}'
classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    '{intended_audience}',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Programming Language :: Python :: 3.11',
    'Programming Language :: Python :: 3 :: Only',
    'License :: OSI Approved :: MIT License',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: MacOS'
]
packages = [{{ include = '{snaked_name}' }}]

[tool.poetry.dependencies]
python = '^3.11'

[build-system]
requires = ['poetry-core']
build-backend = 'poetry.core.masonry.api'
""")
        while not os.path.exists(toml):
            pass


def _add_packages(open_source: bool, is_package: bool) -> None:
    """
    Adds initial packages to pyproject.toml
    :param open_source: Whether project should be open-source
    :param is_package: Whether packages should be installed for the developing a Python package
    :return: None
    """
    os.system('poetry add -D pytest')
    os.system('poetry add -D python-dotenv')

    if not is_package:
        os.system('poetry add loguru')
        return
    elif open_source:
        os.system('poetry add -D build')
        os.system('poetry add -D twine')


def _initialize_folders(
        project_name: str,
        description: str,
        is_package: bool
) -> None:
    """
    Initializes the project folders
    :param project_name: Name of the package
    :param description: The description of the project
    :return: None
    """
    github_user = database.get_github_user()
    snaked_name = snake_case(project_name)
    os.mkdir(snaked_name)
    os.chdir(snaked_name)

    package_files = ['utils.py', 'types.py', 'exceptions.py']
    for filename in package_files:
        open(filename, 'w').close()

    with open('globals.py', 'w') as globals_file:
        globals_file.write("""import os

PACKAGE_PATH = os.path.dirname(os.path.abspath(__file__))
""")

    with open('__init__.py', 'w') as init_file:
        init_file.write(f"""\"\"\"
{project_name}
~~~~~~~~~~~~~~
{description}

:copyright: (c) 2023 by {github_user['name']}
:license: MIT, see LICENSE for more details.
\"\"\"
""")

    os.chdir('../')
    os.mkdir('tests')
    os.chdir('tests')
    open('__init__.py', 'w').close()

    with open('conftest.py', 'w') as conftest_file:
        conftest_file.write('import pytest')

    os.chdir('../')

    with open('LICENSE', 'w') as license_file:
        license_file.write(f"""MIT License

Copyright (c) 2023 {github_user['name']}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""")

        if not is_package:
            with open('config.toml', 'w'):
                pass

            with open('main.py', 'w') as main_file:
                main_file.write("""import loguru
import asyncio


async def main():
    pass


if __name__ == '__main__':
    asyncio.run(main())""")
            with open('globals.py', 'w') as global_file:
                global_file.write(f"""
import os
import tomllib

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
SOURCE_PATH = os.path.join(PROJECT_PATH, '{snaked_name}')
CONFIG_PATH = os.path.join(PROJECT_PATH, "config.toml")
TESTS_PATH = os.path.join(PROJECT_PATH, 'tests')

LOGS_PATH = os.path.join(PROJECT_PATH, "logs")
with open(CONFIG_PATH, 'r') as config:
    content = config.read()
    CONFIG = tomllib.loads(content)
""")


def _add_readme(
        project_name: str,
        description: str,
        open_source: bool,
        is_package: bool
) -> None:
    """
    :param project_name: Name of the package
    :param description: The description of the project
    :param open_source: Whether project should be open-source
    :param is_package: Whether the readme should be configured for the Python package
    :return: None
    """
    github_user = database.get_github_user()
    content = (f"""# {project_name}

[![Croco Logo](https://i.ibb.co/G5Pjt6M/logo.png)](https://t.me/crocofactory)

{description}

- **[Telegram channel](https://t.me/crocofactory)**
- **[Bug reports](https://github.com/{github_user['login']}/{project_name}/issues)**

Source code is made available under the [MIT License](LICENSE)""")

    if is_package:
        content += f'\n\n# Installing {project_name}'

        if open_source:
            content += (f"""
To install `{project_name}` from PyPi, you can use that:

```shell
pip install {project_name}
```
""")
            content += (f"""
To install `{project_name}` from GitHub, use that:

```shell
pip install git+https://github.com/{github_user['login']}/{project_name}.git
```""")
        else:
            content += (f"""
To install `{project_name}` you need to get GitHub API token. After you need to replace this token instead of `<TOKEN>`:

```shell
pip install git+https://<TOKEN>@github.com/{github_user['login']}/{project_name}.git
```""")

    with open('README.md', 'w') as readme_file:
        readme_file.write(content)


@init.command()
@require_github
def package() -> None:
    """Initialize the package directory"""
    repo_name = os.path.basename(os.getcwd())

    description = click.prompt('Enter the package description')

    click.echo('The package will be configured as open-source package')
    open_source = click.confirm('Agree?')

    _add_poetry(repo_name, description, True)
    _add_packages(open_source, True)
    _initialize_folders(repo_name, description, True)
    _add_readme(repo_name, description, open_source, True)


@init.command()
@require_github
def project() -> None:
    """Initialize the project directory"""
    repo_name = os.path.basename(os.getcwd())
    description = click.prompt('Enter the project description')

    _add_poetry(repo_name, description, False)
    _add_packages(False, False)
    _initialize_folders(repo_name, description, False)
    _add_readme(repo_name, description, False, False)
