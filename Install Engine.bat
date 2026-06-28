@echo off
cd /d "%~dp0"
set "CODEX_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

where python >nul 2>nul
if %errorlevel%==0 (
  python -m pip install -U yt-dlp
  if not errorlevel 1 goto end
)

where py >nul 2>nul
if %errorlevel%==0 (
  py -m pip install -U yt-dlp
  if not errorlevel 1 goto end
)

if exist "%CODEX_PY%" (
  "%CODEX_PY%" -m pip install -U yt-dlp
  goto end
)

echo Python was not found.
echo Install Python from https://www.python.org/downloads/
:end
pause
