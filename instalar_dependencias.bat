@echo off
chcp 65001 >nul
title CollageReport144 - Instalar dependencias
cd /d "%~dp0"
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo ERRO: instale Python 3.10+ e marque Add Python to PATH.
  pause
  exit /b 1
)
echo Dependencias instaladas.
pause
