# Didier

[![wakatime](https://wakatime.com/badge/user/3543d4ec-ec93-4b43-abd6-2bc2e310f3c4/project/100156e4-2fb5-40b4-b808-e47ef687905c.svg)](https://wakatime.com/badge/user/3543d4ec-ec93-4b43-abd6-2bc2e310f3c4/project/100156e4-2fb5-40b4-b808-e47ef687905c)

You bet. The time has come.

## Development

Didier uses `Python 3.9.5`, as specified in the [`.python-version`](.python-version)-file. This file will cause [`pyenv`](https://github.com/pyenv/pyenv) to automatically use the correct version when you're working on Didier.

```shell
# Installing Python 3.9.5 through pyenv
pyenv install 3.9.5

# Creating a Virtual Environment and activate it
# PyCharm will automatically activate your venv
python3 -m venv venv
source venv/bin/activate

# Installing dependencies + development dependencies
pip3 install -r requirements.txt -r requirements-dev.txt

# Installing pre-commit hooks
pre-commit install
```

The database can be managed easily using `Docker Compose`. If you want to, however, you can run a regular PostgreSQL server and connect to that instead.

A separate database is used in the tests, as it would obviously not be ideal when tests randomly wipe your database.

```shell
# Starting the database
docker compose up -d

# Starting the database used in tests
docker compose -f docker-compose.test.yml up -d
```

### Commands

```shell
# Starting Didier
python3 main.py

# Running database migrations
alembic upgrade head

# Creating a new database migration
alembic revision --autogenerate -m "Revision message here"

# Running tests
pytest

# Running tests with Coverage
coverage run -m pytest
# Generating code coverage report
coverage html

# Running code quality checks
black
flake8
mypy
```

It's also convenient to have code-formatting happen automatically on-save. The [`Black documentation`](https://black.readthedocs.io/en/stable/integrations/editors.html) explains how to set this up for different types of editors.
