@echo off
title LIPTIS USA SALs App Launcher
cd /d "C:\Users\mohamed.otaify\.gemini\antigravity\scratch\liptis-sals-app"

powershell -Command "try { $res = Invoke-WebRequest -Uri 'http://127.0.0.1:8000/api/health' -TimeoutSec 1 -UseBasicParsing; exit 0 } catch { exit 1 }"
if %ERRORLEVEL% NEQ 0 (
    echo Starting LIPTIS USA SALs App Backend Server...
    cd backend
    start "" "..\.venv\Scripts\pythonw.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
    timeout /t 2 /nobreak >nul
)

echo Opening LIPTIS USA SALs App in your browser...
start http://127.0.0.1:8000
exit
