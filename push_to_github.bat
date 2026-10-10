@echo off
title Publish LIPTIS USA SALs App to GitHub
cd /d "C:\Users\mohamed.otaify\.gemini\antigravity\scratch\liptis-sals-app"

".venv\Scripts\python.exe" push_to_github.py %*

echo.
pause
