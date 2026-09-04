@echo off
setlocal

cd /d "%~dp0"

echo [PackFlow] Creating build environment...
py -3 -m venv .venv
if errorlevel 1 goto :error

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller
if errorlevel 1 goto :error

echo [PackFlow] Building Windows executable...
pyinstaller --noconfirm --clean --windowed --name PackFlow --collect-all PySide6 --collect-all reportlab --collect-all PIL main.py
if errorlevel 1 goto :error

echo.
echo Build complete.
echo Executable: dist\PackFlow\PackFlow.exe
exit /b 0

:error
echo.
echo Build failed.
exit /b 1
