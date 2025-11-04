# CAFEX Monorepo Developer Guide

This document provides information for developers working on the CAFEX monorepo.

### Project Structure

The CAFEX monorepo is organized as follows:

```
cafex
├── libs/
│   ├── cafex/
│   ├── cafex_api/
│   ├── cafex_core/
│   ├── cafex_db/
│   └── cafex_ui/
│   └── cafex_desktop/
├── scripts/
│   ├── build_package.py
│   └── versioning.py
├── dev-requirements.txt
├── pip-requirements.txt
├── DEV-README.md
├── README.md
├── build_package.py
├── tox.ini
├── toxtool.toml
└── ... (other project files)
```
- **libs:** Contains the source code for all CAFEX packages.
- **scripts:** Contains versioning script.
- **dev-requirements.txt:** Lists additional dependencies required for development (e.g., testing tools).
- **pip-requirements.txt:** Lists pip version dependency.
- **build_package.py:** Script for building the package.
- **tox.ini:**  Configuration for running tests, linting, and other development tasks using Tox.
- **toxtool.toml:**  Common tool configuration file for the entire monorepo project (Black, isort, pylint, etc.).

### Getting Started

#### Prerequisites

- Python 3.12 or later
- pip 24 or later (Python package manager)

#### Editable Installation

To install the packages in editable mode, allowing you to make changes and see them reflected immediately, use the following commands:

1. Install development dependencies: `pip install -r dev-requirements.txt`
2. Install each package in editable mode:
   * `pip install -e libs/cafex_core/`
   * `pip install -e libs/cafex_api/`
   * `pip install -e libs/cafex_db/`
   * `pip install -e libs/cafex_ui/`
   * `pip install -e libs/cafex_desktop/`
   * `pip install -e libs/cafex/`
   
### Building Wheels

To build wheel files for individual packages (e.g., for distribution or deployment), use the `build_package.py` script from the project root:

**Usage:**
- Bump minor version for cafex_api and build: `python build_package.py cafex_api --bump minor`
- Set specific version for cafex_db and build: `python build_package.py cafex_db --version 1.0.0`
- Use version specified in `cafex_api.__init__.py`: `python build_package.py cafex_api`

**Bump level examples:**
- major: `Will change 0.0.10 to 1.0.0`
- minor: `Will change 0.0.10 to 0.1.0`
- patch: `Will change 0.0.10 to 0.0.11`


## Using Tox

Tox is a tool for automating testing, linting, and other development tasks in isolated environments.

**Running Tox:**
- **Run all environments:**  `tox` 
- **Run a specific environment:** `tox -e <environment_name>`  (e.g., `tox -e cafex-api-build`)
- **Run environments in parallel:** `tox -p auto` (or `tox -p <number_of_processes>`)

#### Important Tox Commands

- **`tox -e cafex-api-build`:**  Runs linting, tests, coverage, and builds the `cafex-api` package, bumping the patch version. 
- **`tox -e cafex-db-build`:**  Runs the same process for the `cafex-db` package. 
- **`tox -e cafex-ui-build`:** Runs the same process for the `cafex-ui` package.
- **`tox -e cafex-core-build`:** Runs the same process for the `cafex-core` package. 
- **`tox -e cafex-desktop-build`:** Runs the same process for the `cafex-desktop` package. 
- **`tox -e coverage-report`:**  Combines the coverage reports from all packages and generates a combined report. 

#### Example Tox Usage

To build all packages in parallel, each with an incremented patch version:

```bash
tox -p auto