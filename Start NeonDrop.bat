@echo off
cd /d "%~dp0"
set "CODEX_PY=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

where python >nul 2>nul
if %errorlevel%==0 (
  python app.py
  if not errorlevel 1 goto end
)

where py >nul 2>nul
if %errorlevel%==0 (
  py app.py
  if not errorlevel 1 goto end
)

if exist "%CODEX_PY%" (
  "%CODEX_PY%" app.py
  goto end
)

echo NeonDrop needs Python to run.
echo Install Python from https://www.python.org/downloads/
echo Then run this file again.
:end
pause
