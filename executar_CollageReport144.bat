@echo off
chcp 65001 >nul
title CollageReport144
cd /d "%~dp0"
py CollageReport144.py
if errorlevel 1 (
  echo Nao foi possivel iniciar. Execute instalar_dependencias.bat primeiro.
  pause
)
