@echo off
title SnapClass - Public Sharing Launcher
echo ====================================================================
echo             SnapClass - Public Mobile Sharing Link
echo ====================================================================
cd /d "%~dp0"

echo [1/2] Starting Main Streamlit App in background...
start /b app\venv\Scripts\streamlit.exe run app\app.py --server.headless true --server.port 8501

echo [2/2] Connecting Cloudflare Tunnel to generate public HTTPS link...
echo.
echo Look for the link ending in .trycloudflare.com below.
echo Copy and share that link to open on mobile phones or any computer!
echo ====================================================================
echo.

.\cloudflared.exe tunnel --protocol http2 --url http://localhost:8501
pause
