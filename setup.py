#!/usr/bin/env python3
"""Setup script for CredentialForge."""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="credentialforge",
    version="0.1.0",
    author="CredentialForge Contributors",
    author_email="maintainers@credentialforge.org",
    description="Synthetic document generation with embedded credentials for security testing",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/credential-forge",
    project_urls={
        "Bug Reports": "https://github.com/your-org/credential-forge/issues",
        "Source": "https://github.com/your-org/credential-forge",
        "Documentation": "https://github.com/your-org/credential-forge/docs",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: Security",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.3.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
            "mypy>=1.3.0",
            "pre-commit>=3.3.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "myst-parser>=2.0.0",
        ],
        "llm": [
            "llama-cpp-python>=0.2.0",
            "langchain>=0.1.0",
            "langchain-community>=0.0.10",
        ],
    },
    entry_points={
        "console_scripts": [
            "credentialforge=credentialforge.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "credentialforge": [
            "data/*.json",
            "data/*.yaml",
            "templates/*.txt",
        ],
    },
    keywords=[
        "security",
        "testing",
        "credentials",
        "synthetic",
        "documentation",
        "llm",
        "ai",
        "penetration-testing",
        "vulnerability-assessment",
    ],
    zip_safe=False,
)
