from setuptools import setup, find_packages
import os

VERSION = "0.1.0"  # Matches pyproject.toml

def get_long_description():
    with open(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"),
        encoding="utf8",
    ) as fp:
        return fp.read()

setup(
    name="shell-sage",
    description="ShellSage: AI-powered shell commands in your terminal (Fork from https://github.com/AnswerDotAI/shell_sage)",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    author="Nicolay Gerold",
    author_email="nicolay.gerold@gmail.com",
    license="Apache License, Version 2.0",
    version=VERSION,
    packages=find_packages(),
    entry_points={
        "console_scripts": ["ssage=shell_sage.core:app"]
    },
    install_requires=[
        "aisuite>=0.1.6",
        "anthropic>=0.40.0",
        "openai>=1.57.0",
        "rich>=13.9.4",
        "typer>=0.15.1",
    ],
    extras_require={
        "dev": [
            "isort>=5.13.2",
            "pytest",
        ]
    },
    python_requires=">=3.12",
)
