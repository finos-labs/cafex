@echo off
REM CAFEX Installer Script
SETLOCAL ENABLEDELAYEDEXPANSION

REM Set repo URL and clone destination
SET REPO_URL=https://github.com/finos-labs/cafex.git
SET REPO_DIR=cafex

REM Clone CAFEX repo
git clone %REPO_URL%
cd %REPO_DIR%

REM Create Python virtual environment (recommended)
python -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate

REM Upgrade pip to latest version
python -m pip install --upgrade pip

REM Install dev dependencies
pip install -r dev-requirements.txt

REM Install CAFEX packages (optional, for modular usage)
pip install cafex cafex-ui cafex-api cafex-db cafex-core

REM Deactivate virtual environment (optional)
REM deactivate

@echo.
@echo Done! CAFEX dependencies are installed.
@echo To activate your virtual environment again, run:
@echo venv\Scripts\activate
@echo.
pause
