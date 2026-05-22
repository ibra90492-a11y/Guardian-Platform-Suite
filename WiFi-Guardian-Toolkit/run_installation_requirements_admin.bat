@echo off
setlocal
set "SCRIPT=%~dp0installation_requirements.ps1"

powershell -NoProfile -Command "Start-Process PowerShell -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File \"%SCRIPT%\"'"

endlocal
