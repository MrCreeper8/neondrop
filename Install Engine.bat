@echo off
setlocal
cd /d "%~dp0"

where python >nul 2>nul
if %errorlevel%==0 (
  python -m pip install -U yt-dlp
  pause
  exit /b
)

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 -m pip install -U yt-dlp
  pause
  exit /b
)

echo Python was not found.
echo Install Python from https://www.python.org/downloads/
pause
exit /b 1
