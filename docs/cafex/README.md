CAFEX Monorepo Documentation
Overview

The CAFEX Monorepo contains multiple Python packages for automation testing:

Package	Description
cafex-core	Provides foundational functionalities and utilities for automation.
cafex-api	Tools for API testing, including request building, response parsing, and assertions.
cafex-db	Database testing support for MSSQL, MySQL, Oracle, Hive, Postgres, and Cassandra.
cafex-ui	Web UI and mobile app testing, including driver management, element interactions, and assertions.
cafex	Meta-package containing all the above packages.

CAFEX (Core Automation Framework Enhancements) is designed to simplify and streamline various testing tasks with a Python-based framework.

Getting Started
Prerequisites

Python 3.12 or later

pip 24 or later (Python package manager)

Installation

Clone the repository:

git clone <repo-url>
cd cafex-monorepo


Install development dependencies:

pip install -r dev-requirements.txt


Install the CAFEX packages as needed:

Use Case	Command
Full stack (UI, API, DB)	pip install cafex
UI Testing only	pip install cafex-ui
API Testing only	pip install cafex-api
Database Testing only	pip install cafex-db
Core modules only	pip install cafex-core
Package Details

For more information, refer to the individual README files:

CAFEX Super Package: libs/cafex/README.md

CAFEX Core: libs/cafex_core/README.md

CAFEX API: libs/cafex_api/README.md

CAFEX DB: libs/cafex_db/README.md

CAFEX UI: libs/cafex_ui/README.md

Optional: Quick Start Example
# Example: API testing using cafex-api
from cafex_api.client import ApiClient

client = ApiClient(base_url="https://api.example.com")
response = client.get("/status")
assert response.status_code == 200

Tips

Use the super package cafex if you need all functionalities at once.

Install packages individually if you only need specific modules.

Check the respective README files for detailed usage examples.

✅ This version is cleaner, more structured, and beginner-friendly, while keeping all original information.
