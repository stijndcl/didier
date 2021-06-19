# FAQ
Answers to Frequently Asked Questions and solutions to issues that may arise.

## Issues installing dotenv

The name of this package is `python-dotenv`, as listed in `requirements.txt`. The _name_ of the package, however, is just `dotenv`. This confuses PyCharm, which will tell you that you don't have `dotenv` installed as it can't link those two together. You can just click `ignore this requirement` if you don't like the warning.

## Issues installing psycopg2

The `psychopg2` and `psychopg2-binary` packages might cause you some headaches when trying to install them, especially when using PyCharm to install dependencies. The reason for this is because these are `PSQL` packages, and as a result they require you to have `PSQL` installed on your system to function properly.

## Package is not listed in project requirements

This is the exact same case as [Issues installing dotenv](#issues-installing-dotenv), and occurs for packages such as `Quart`. The names of the modules differ from the name used to install it from `pip`. Once again, you can ignore this message.