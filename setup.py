from setuptools import setup, find_packages

setup(
    name="gruntkill",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer", "rich", "anthropic", "watchdog", "python-dotenv", "slack-sdk"
    ],
    entry_points={
        "console_scripts": [
            "gk=cli.main:cli",
        ],
    },
)
