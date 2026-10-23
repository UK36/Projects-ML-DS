@echo off
echo ========================================================
echo Starting SnapClass - Landing Page (Flask)
echo ========================================================
cd /d "%~dp0landing"
if exist ..\app\venv\Scripts\activate.bat (
    call ..\app\venv\Scripts\activate.bat
)
python app.py
pause
