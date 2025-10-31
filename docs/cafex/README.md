# CAFEX Monorepo

This monorepo contains the following CAFEX packages:

- **cafex-core:** The core package providing foundational functionalities and utilities.
- **cafex-api:** Package for API testing, including request building, response parsing, and assertion methods.
- **cafex-db:** Package for database testing, supporting various databases like MSSQL, MySQL, Oracle, Hive, Postgres, and Cassandra.
- **cafex-ui:** Package for web UI and mobile app testing, including driver management, element interaction, and assertion methods.
- **cafex:** The super package containing all the above packages

## Introduction

CAFEX (Centralized Automation Framework Enabler) is a Python-based automation framework designed to simplify and streamline various testing tasks. This monorepo structure allows for efficient management and development of all CAFEX packages in a single location.

## Getting Started

### Prerequisites

- Python 3.12 or later
- pip 24 or later(Python package manager)

### Installation

1. Clone or download the CAFEX monorepo.
2. Install the required dependencies using pip: ```pip install -r dev-requirements.txt```

**Dependencies:**
- For UI, API and DB testing: `pip install cafex`
- For UI testing: `pip install cafex-ui`
- For DB testing: `pip install cafex-db`
- For API testing: `pip install cafex-api`
- For Core modules: `pip install cafex-core`

## Package Details

For detailed information about each package, please refer to their respective README files:

- **cafex:** libs/cafex/README.md
- **cafex-api:** libs/cafex_api/README.md
- **cafex-db:** libs/cafex_db/README.md
- **cafex-ui:** libs/cafex_ui/README.md
- **cafex-core:** libs/cafex_core/README.md
