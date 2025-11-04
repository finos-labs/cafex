@echo off
setlocal

echo Choose installer (pip or uv)
set /p installer=

echo Enter package to install (ui, db, api, desktop, all)
set /p pkgtype=


echo Enter full path to python.exe e.g: C:\Python312\python.exe..
    set /p python_path=

if /i "%installer%"=="pip" (
    if /i "%pkgtype%"=="ui" (
        "%python_path%" -m pip install cafex-ui
    ) else if /i "%pkgtype%"=="db" (
        "%python_path%" -m pip install cafex-db
    ) else if /i "%pkgtype%"=="api" (
        "%python_path%" -m pip install cafex-api
    ) else if /i "%pkgtype%"=="desktop" (
        "%python_path%" -m pip install cafex-desktop
    ) else if /i "%pkgtype%"=="all" (
        "%python_path%" -m pip install cafex
    ) else (
        echo Invalid package option. Please enter one of: ui, db, api, desktop, all.
    )
) else if /i "%installer%"=="uv" (
    pip install uv
    if not "%python_path%"=="" (
        uv venv --python "%python_path%" venv
    ) else (
        uv venv venv
    )
    call venv\Scripts\activate
    if /i "%pkgtype%"=="ui" (
        uv pip install cafex-ui
    ) else if /i "%pkgtype%"=="db" (
        uv pip install cafex-db
    ) else if /i "%pkgtype%"=="api" (
        uv pip install cafex-api
    ) else if /i "%pkgtype%"=="desktop" (
        uv pip install cafex-desktop
    ) else if /i "%pkgtype%"=="all" (
        uv pip install cafex
    ) else (
        echo Invalid package option. Please enter one of: ui, db, api, desktop, all.
    )
) else (
    echo Invalid installer option. Please enter either pip or uv.
)

pause
endlocal
