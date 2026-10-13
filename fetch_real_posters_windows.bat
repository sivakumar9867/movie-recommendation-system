@echo off
cd /d "%~dp0"
if not exist "venv\Scripts\python.exe" call setup_windows.bat
if not exist "venv\Scripts\python.exe" exit /b 1

echo.
echo Paste your TMDB API key (themoviedb.org - Settings - API - "API Key"),
echo then press Enter. Run this file again if some posters fail.
set /p TMDB_API_KEY=API key: 
"venv\Scripts\python.exe" fetch_posters.py
echo.
echo Done. Start the app with run_windows.bat and press Ctrl+F5 in the browser.
pause
