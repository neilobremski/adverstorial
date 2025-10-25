#!/usr/bin/env python3
"""Setup script for adverstorial."""

from setuptools import setup, find_packages

setup(
    name="adverstorial",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.21.0",
    ],
    entry_points={
        "console_scripts": [
            "adverstorial=adverstorial.cli:main",
        ],
    },
    python_requires=">=3.8",
)
