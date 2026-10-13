@echo off
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" call setup_windows.bat
if not exist "venv\Scripts\python.exe" exit /b 1

if not exist static\posters\rrr.svg "venv\Scripts\python.exe" generate_posters.py

echo.
echo Open http://127.0.0.1:5000 in your browser  (press Ctrl+C here to stop)
"venv\Scripts\python.exe" app.py
pause
