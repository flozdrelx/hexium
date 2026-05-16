@echo off
setlocal
cd Scripts
if not exist "venv" (
    echo Creating venv...
    python -m venv venv >nul 2>&1
)
echo Installing packages, please wait...
call venv\Scripts\activate && python -m pip install -r requirements.txt >nul 2>&1
echo Ready!
python main.py
pause