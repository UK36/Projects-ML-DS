@echo off
title Push SnapClass to GitHub
cd /d "%~dp0"
echo ====================================================================
echo             Push SnapClass to GitHub
echo ====================================================================
echo.
echo Target Repository: https://github.com/UK36/snapclass-project.git
echo.
echo (Make sure you have created the repository 'snapclass-project' on github.com)
echo.
git push -u origin main
echo.
echo ====================================================================
pause
