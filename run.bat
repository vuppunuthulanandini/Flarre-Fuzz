@echo off
REM One-command launcher for Windows
cd /d "%~dp0"
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
echo Starting Flarre-Fuzz at http://127.0.0.1:8000 ...
python -m flarre_fuzz
