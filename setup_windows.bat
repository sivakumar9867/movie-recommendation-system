@echo off
REM One-time setup: creates the "venv" folder INSIDE this project and installs the packages.
cd /d "%~dp0"

if exist "venv\Scripts\python.exe" goto install

echo Creating the project environment (one time)...
set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY python --version >nul 2>&1 && set "PY=python"
if not defined PY if exist "C:\Users\admin\Downloads\movie-recommendation-system-main\movie-recommendation-system-main\venv\Scripts\python.exe" set "PY=C:\Users\admin\Downloads\movie-recommendation-system-main\movie-recommendation-system-main\venv\Scripts\python.exe"

if not defined PY (
    echo.
    echo Python was not found on this computer.
    echo Install it from https://www.python.org/downloads/ and tick "Add python.exe to PATH",
    echo then double-click this file again.
    pause
    exit /b 1
)

%PY% -m venv venv
if errorlevel 1 (
    echo Could not create the environment.
    pause
    exit /b 1
)

:install
"venv\Scripts\python.exe" -c "import flask, pandas, sklearn" >nul 2>&1
if errorlevel 1 (
    echo Installing packages (needs internet, one time)...
    "venv\Scripts\python.exe" -m pip install -r requirements.txt
)
echo Setup complete.
