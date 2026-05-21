@echo off
setlocal
cd /d "%~dp0Scripts" || (
    echo Could not find Scripts directory.
    exit /b 1
)

if not exist "venv" (
    echo Creating venv...
    python -m venv venv
    if errorlevel 1 exit /b 1
)

call venv\Scripts\activate
if errorlevel 1 exit /b 1

python -m pip install -r requirements.txt --disable-pip-version-check >nul
if errorlevel 1 exit /b 1

echo Ready!
python main.py
pause