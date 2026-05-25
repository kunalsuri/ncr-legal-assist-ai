@echo off
setlocal EnableDelayedExpansion

:: ============================================================================
::  NCR Legal Assist AI — Windows Launch Script
::
::  Double-click this file to perform a full pre-flight check and start the
::  Streamlit application.
::
::  Checks performed (in order):
::    1. PowerShell available  → hands off to run.ps1 (preferred path)
::    2. Python >= 3.11 in PATH
::    3. .venv virtual environment (creates if absent)
::    4. Python packages installed (installs from pyproject.toml if absent)
::    5. Ollama LLM backend  (starts if not running)
::    6. Qdrant vector DB     (advisory only — optional for RAG mode)
::
::  Then launches:  streamlit run src/app/streamlit_app.py
::
::  Requirements: Python >= 3.11, Ollama, Docker (optional, for Qdrant)
:: ============================================================================

title NCR Legal Assist AI — Pre-flight Check ^& Launch

:: ── Repo root is the directory containing this .bat file ────────────────────
set "REPO_ROOT=%~dp0"
:: Strip trailing backslash
if "%REPO_ROOT:~-1%"=="\" set "REPO_ROOT=%REPO_ROOT:~0,-1%"

set "VENV_DIR=%REPO_ROOT%\.venv"
set "VENV_PYTHON=%VENV_DIR%\Scripts\python.exe"
set "VENV_STREAMLIT=%VENV_DIR%\Scripts\streamlit.exe"
set "APP_ENTRY=src\app\streamlit_app.py"
set "PS1_SCRIPT=%REPO_ROOT%\run.ps1"
set "OLLAMA_URL=http://localhost:11434"
set "QDRANT_URL=http://localhost:6333"
set "PYTHON_REQUIRED_MAJOR=3"
set "PYTHON_REQUIRED_MINOR=11"

echo.
echo  ========================================================================
echo   NCR Legal Assist AI  *  Pre-flight Check ^& Launch
echo  ========================================================================
echo.

:: ── Change to repo root ──────────────────────────────────────────────────────
cd /d "%REPO_ROOT%"
if not exist "pyproject.toml" (
    echo  [FAIL] pyproject.toml not found.
    echo  [INFO] This script must be placed in the repository root directory.
    goto :end_pause
)

:: ── Preferred path: delegate to run.ps1 via PowerShell ──────────────────────
::
::  PowerShell gives richer output (colours, better HTTP checks, progress bars).
::  If it is available and run.ps1 is present, hand off immediately.
::
where powershell.exe >nul 2>&1
if not errorlevel 1 (
    if exist "%PS1_SCRIPT%" (
        echo  [INFO] PowerShell found. Handing off to run.ps1 for best experience.
        echo  [INFO] If you see a security prompt, choose "Run once".
        echo.
        powershell.exe -NoProfile -NonInteractive ^
            -ExecutionPolicy Bypass ^
            -File "%PS1_SCRIPT%"
        goto :eof
    )
)

:: ── Fallback: native batch pre-flight ───────────────────────────────────────
echo  [INFO] Proceeding with native batch pre-flight (PowerShell not available).
echo.

:: ────────────────────────────────────────────────────────────────────────────
:: [1] Python
:: ────────────────────────────────────────────────────────────────────────────
echo  [Python]

where python >nul 2>&1
if errorlevel 1 (
    echo  [FAIL] python.exe not found in PATH.
    echo  [INFO] Install Python ^>= 3.11 from https://www.python.org/downloads/
    echo  [INFO] Ensure "Add Python to PATH" is checked during installation.
    goto :end_pause
)

:: Parse major.minor from "Python X.Y.Z"
for /f "tokens=2" %%V in ('python --version 2^>^&1') do set "PYVER=%%V"
for /f "tokens=1,2 delims=." %%A in ("!PYVER!") do (
    set "PYMAJ=%%A"
    set "PYMIN=%%B"
)

if not defined PYMAJ goto :python_parse_fail
if not defined PYMIN  goto :python_parse_fail

if !PYMAJ! LSS %PYTHON_REQUIRED_MAJOR% goto :python_old
if !PYMAJ! EQU %PYTHON_REQUIRED_MAJOR% if !PYMIN! LSS %PYTHON_REQUIRED_MINOR% goto :python_old

echo  [OK]   Python !PYVER!
goto :check_venv

:python_parse_fail
echo  [FAIL] Could not parse Python version (got: !PYVER!).
goto :end_pause

:python_old
echo  [FAIL] Python !PYVER! found, but ^>= %PYTHON_REQUIRED_MAJOR%.%PYTHON_REQUIRED_MINOR% is required.
echo  [INFO] Install Python ^>= 3.11 from https://www.python.org/downloads/
goto :end_pause

:: ────────────────────────────────────────────────────────────────────────────
:: [2] Virtual environment
:: ────────────────────────────────────────────────────────────────────────────
:check_venv
echo.
echo  [Virtual Environment (.venv)]

if not exist "%VENV_DIR%\" (
    echo  [....] .venv not found. Creating virtual environment ...
    python -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo  [FAIL] python -m venv failed.
        echo  [INFO] Ensure python.exe has write access to: %REPO_ROOT%
        goto :end_pause
    )
    echo  [OK]   .venv created.
) else (
    echo  [OK]   .venv directory found.
)

if not exist "%VENV_PYTHON%" (
    echo  [FAIL] %VENV_PYTHON% missing.
    echo  [INFO] Delete the .venv folder and re-run this script.
    goto :end_pause
)

for /f "tokens=2" %%V in ('"%VENV_PYTHON%" --version 2^>^&1') do (
    echo  [OK]   venv Python %%V
)

:: ────────────────────────────────────────────────────────────────────────────
:: [3] Python packages
:: ────────────────────────────────────────────────────────────────────────────
echo.
echo  [Python Packages]

"%VENV_PYTHON%" -c "import streamlit" >nul 2>&1
if not errorlevel 1 (
    echo  [OK]   Packages present (streamlit canary import OK).
    goto :check_ollama
)

echo  [....] Packages not found. Running: pip install -e .[dev]
echo  [INFO] This may take several minutes on first run ...

"%VENV_PYTHON%" -m pip install --upgrade pip --quiet
"%VENV_PYTHON%" -m pip install -e ".[dev]"
if errorlevel 1 (
    echo  [FAIL] pip install failed.
    echo  [INFO] Check your internet connection and pyproject.toml.
    goto :end_pause
)

:: Verify canary again
"%VENV_PYTHON%" -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo  [FAIL] Installation completed but streamlit still cannot be imported.
    goto :end_pause
)

echo  [OK]   All packages installed successfully.

:: ────────────────────────────────────────────────────────────────────────────
:: [4] Ollama (LLM backend)
:: ────────────────────────────────────────────────────────────────────────────
:check_ollama
echo.
echo  [Ollama  (LLM backend — %OLLAMA_URL%)]

:: curl ships with Windows 10/11. -f = fail on HTTP 4xx/5xx, -s = silent.
curl -s -f --connect-timeout 4 --max-time 6 "%OLLAMA_URL%/api/tags" >nul 2>&1
if not errorlevel 1 (
    echo  [OK]   Ollama is running.
    goto :check_qdrant
)

echo  [WARN] Ollama is not responding. Attempting to start it ...

where ollama >nul 2>&1
if errorlevel 1 (
    echo  [FAIL] ollama.exe not found in PATH.
    echo  [INFO] Download from https://ollama.com/download
    echo  [INFO] After installing, run:  ollama pull llama3.2
    echo  [WARN] The app will open but LLM features will be disabled.
    goto :check_qdrant
)

:: Start ollama serve in a detached window (minimised)
start "" /B ollama serve >nul 2>&1

echo  [....] Waiting for Ollama to become ready (up to 25 seconds) ...
set /a OLLAMA_WAIT=0

:ollama_wait_loop
timeout /t 1 /nobreak >nul
set /a OLLAMA_WAIT+=1
curl -s -f --connect-timeout 2 --max-time 3 "%OLLAMA_URL%/api/tags" >nul 2>&1
if not errorlevel 1 (
    echo  [OK]   Ollama started after !OLLAMA_WAIT!s.
    goto :check_qdrant
)
if !OLLAMA_WAIT! LSS 25 goto :ollama_wait_loop

echo  [WARN] Ollama did not respond within 25s.
echo  [INFO] LLM features will be unavailable until Ollama is running.
echo  [INFO] Start it manually in a separate terminal:  ollama serve

:: ────────────────────────────────────────────────────────────────────────────
:: [5] Qdrant (vector DB — optional)
:: ────────────────────────────────────────────────────────────────────────────
:check_qdrant
echo.
echo  [Qdrant  (vector DB — %QDRANT_URL%  — optional)]

curl -s -f --connect-timeout 4 --max-time 6 "%QDRANT_URL%/readyz" >nul 2>&1
if not errorlevel 1 (
    echo  [OK]   Qdrant is running.
    goto :launch
)

echo  [WARN] Qdrant is not running.  RAG retrieval will be unavailable.
echo  [INFO] Start it with:  docker compose up -d qdrant
echo  [INFO] General-chat mode works without Qdrant.

:: ────────────────────────────────────────────────────────────────────────────
:: [6] Launch Streamlit
:: ────────────────────────────────────────────────────────────────────────────
:launch
echo.
echo  ========================================================================
echo   All checks complete. Launching application ...
echo  ========================================================================
echo.
echo  [OK]   Starting Streamlit at http://localhost:8501
echo.
echo  Press Ctrl+C in this window to stop the application.
echo.

if exist "%VENV_STREAMLIT%" (
    "%VENV_STREAMLIT%" run "%APP_ENTRY%" --server.headless false
) else (
    :: Fallback — invoke as a module (always available when streamlit is installed)
    "%VENV_PYTHON%" -m streamlit run "%APP_ENTRY%" --server.headless false
)

:: Streamlit has exited (Ctrl+C or error)
echo.
echo  Application stopped.

:end_pause
echo.
pause
endlocal
