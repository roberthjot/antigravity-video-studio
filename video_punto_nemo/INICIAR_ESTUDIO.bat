@echo off
title Antigravity Video Studio
echo ===================================================
echo     Iniciando Antigravity Video Studio Local
echo ===================================================
echo.
cd /d "%~dp0studio"
start http://127.0.0.1:8080
python studio_server.py
pause
