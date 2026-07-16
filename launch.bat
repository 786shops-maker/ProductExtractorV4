@echo off
title Product Extractor V3
echo ========================================
echo   Starting Product Extractor...
echo ========================================
echo.

:: Start Flask server in background
start /B python app.py

:: Wait for server to start
timeout /t 3 /nobreak >nul

:: Open browser to welcome page
start http://127.0.0.1:5000/

echo.
echo Server is running at http://127.0.0.1:5000/
echo Press Ctrl+C to stop the server.
echo.

:: Keep window open
pause