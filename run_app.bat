@echo off
echo ========================================================
echo Starting SnapClass - AI Attendance Application
echo ========================================================
cd /d "%~dp0app"
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found in app\venv. Using system Python...
)
streamlit run app.py
pause
