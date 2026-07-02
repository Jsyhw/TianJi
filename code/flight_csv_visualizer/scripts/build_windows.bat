@echo off
cd /d "%~dp0\.."
pyinstaller --noconfirm --clean FlightCSVVisualizer.spec
