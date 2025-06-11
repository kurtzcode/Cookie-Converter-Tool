@echo off
chcp 65001 >nul
cls
title Cookie Converter

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║                    COOKIE CONVERTER TOOL                 ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.

REM Executa o script Python
python CookiesConvert.py

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║               Conversion completed successfully!         ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
pause >nul
