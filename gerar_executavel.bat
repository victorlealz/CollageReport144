@echo off
chcp 65001 >nul
title CollageReport144 - Gerar EXE
cd /d "%~dp0"
py -m pip install -r requirements.txt
if errorlevel 1 (
  echo Falha ao instalar dependencias. Verifique Python e internet.
  pause
  exit /b 1
)
py -m PyInstaller --noconfirm --clean --onefile --windowed --name CollageReport144 CollageReport144.py
if errorlevel 1 (
  echo Falha ao gerar o executavel.
  pause
  exit /b 1
)
echo CONCLUIDO: dist\CollageReport144.exe
pause
