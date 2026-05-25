#Requires -Version 5.1
<#
.SYNOPSIS
    NCR Legal Assist AI — Windows launch script (PowerShell).

.DESCRIPTION
    Performs a full pre-flight check, then starts the Streamlit application.

    Checks performed (in order):
      1. Working directory set to repo root
      2. Python >= 3.11 available in PATH
      3. .venv exists (creates it if not)
      4. Required packages installed (installs from pyproject.toml if not)
      5. Ollama LLM backend reachable (starts it if not running)
      6. Qdrant vector DB reachable (informs if not — optional for RAG mode)

    Usage:
      Double-click  : right-click → "Run with PowerShell"
      Terminal      : .\run.ps1
      Admin terminal: PowerShell -ExecutionPolicy Bypass -File .\run.ps1

.NOTES
    Requires Python >= 3.11, Ollama, and (optionally) Docker for Qdrant.
    Internet access needed on first run to download packages and models.
#>

[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

$REPO_ROOT          = Split-Path -Parent $MyInvocation.MyCommand.Definition
$VENV_DIR           = Join-Path $REPO_ROOT '.venv'
$VENV_PYTHON        = Join-Path $VENV_DIR  'Scripts\python.exe'
$VENV_STREAMLIT     = Join-Path $VENV_DIR  'Scripts\streamlit.exe'
$APP_ENTRY          = Join-Path $REPO_ROOT 'src\app\streamlit_app.py'
$PYPROJECT          = Join-Path $REPO_ROOT 'pyproject.toml'
$CANARY_PACKAGE     = 'streamlit'
$OLLAMA_TAGS_URL    = 'http://localhost:11434/api/tags'
$QDRANT_HEALTH_URL  = 'http://localhost:6333/readyz'
$PYTHON_MIN_VER     = [version]'3.11'
$OLLAMA_START_WAIT  = 25    # seconds to wait for Ollama to become ready
$BAR                = '─' * 72

# ─────────────────────────────────────────────────────────────────────────────
# Output helpers
# ─────────────────────────────────────────────────────────────────────────────

function Write-Banner {
    Write-Host ''
    Write-Host $BAR                                          -ForegroundColor DarkCyan
    Write-Host '  NCR Legal Assist AI  ·  Pre-flight Check & Launch'  -ForegroundColor Cyan
    Write-Host $BAR                                          -ForegroundColor DarkCyan
    Write-Host ''
}

function Write-Section([string]$title) {
    Write-Host ''
    Write-Host "  [$title]" -ForegroundColor DarkYellow
}

function Write-OK  ([string]$msg) { Write-Host "  [OK]   $msg" -ForegroundColor Green  }
function Write-Info([string]$msg) { Write-Host "  [INFO] $msg" -ForegroundColor Cyan   }
function Write-Warn([string]$msg) { Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function Write-Fail([string]$msg) { Write-Host "  [FAIL] $msg" -ForegroundColor Red    }
function Write-Step([string]$msg) { Write-Host "  [....] $msg" -ForegroundColor Gray   }

function Exit-WithPause([int]$code = 1) {
    Write-Host ''
    Write-Host '  Pre-flight failed. Press any key to close this window ...' `
        -ForegroundColor DarkGray
    try { $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown') } catch {}
    exit $code
}

# ─────────────────────────────────────────────────────────────────────────────
# HTTP helper  (no WebClient; uses .NET HttpClient for reliability)
# ─────────────────────────────────────────────────────────────────────────────

function Test-UrlReachable([string]$url, [int]$timeoutSec = 4) {
    try {
        $req = [System.Net.HttpWebRequest]::CreateHttp($url)
        $req.Timeout         = $timeoutSec * 1000
        $req.Method          = 'GET'
        $req.AllowAutoRedirect = $true
        $resp = $req.GetResponse()
        $sc   = [int]$resp.StatusCode
        $resp.Dispose()
        return ($sc -ge 200 -and $sc -lt 400)
    } catch {
        return $false
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 1 — Working directory
# ─────────────────────────────────────────────────────────────────────────────

function Set-RepoRoot {
    Write-Section 'Working Directory'

    if (-not (Test-Path $PYPROJECT)) {
        Write-Fail "pyproject.toml not found. Script must live in the repo root."
        Exit-WithPause
    }

    Set-Location $REPO_ROOT
    Write-OK "Repo root: $REPO_ROOT"
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 2 — Python version
# ─────────────────────────────────────────────────────────────────────────────

function Assert-PythonVersion {
    Write-Section 'Python'

    $pythonExe = $null
    foreach ($candidate in @('python', 'python3', 'py')) {
        if (Get-Command $candidate -ErrorAction SilentlyContinue) {
            $pythonExe = $candidate
            break
        }
    }

    if (-not $pythonExe) {
        Write-Fail 'Python not found in PATH.'
        Write-Info  "Install Python >= $PYTHON_MIN_VER from https://www.python.org/downloads/"
        Write-Info  'Ensure "Add Python to PATH" is checked during install.'
        Exit-WithPause
    }

    $raw = & $pythonExe --version 2>&1
    if ($raw -notmatch 'Python\s+(\d+\.\d+(?:\.\d+)?)') {
        Write-Fail "Could not parse Python version from: $raw"
        Exit-WithPause
    }

    $installed = [version]($Matches[1])
    if ($installed -lt $PYTHON_MIN_VER) {
        Write-Fail "Python $installed found, but >= $PYTHON_MIN_VER is required."
        Write-Info  "Install Python >= $PYTHON_MIN_VER from https://www.python.org/downloads/"
        Exit-WithPause
    }

    Write-OK "Python $installed  ($pythonExe)"
    return $pythonExe
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 3 — Virtual environment
# ─────────────────────────────────────────────────────────────────────────────

function Assert-Venv([string]$pythonExe) {
    Write-Section 'Virtual Environment (.venv)'

    if (-not (Test-Path $VENV_DIR)) {
        Write-Step 'Virtual environment not found. Creating .venv ...'
        & $pythonExe -m venv $VENV_DIR
        if ($LASTEXITCODE -ne 0) {
            Write-Fail 'python -m venv failed.'
            Exit-WithPause
        }
        Write-OK '.venv created.'
    } else {
        Write-OK '.venv directory found.'
    }

    if (-not (Test-Path $VENV_PYTHON)) {
        Write-Fail "$VENV_PYTHON missing. Delete .venv and re-run."
        Exit-WithPause
    }

    $venvVer = & $VENV_PYTHON --version 2>&1
    Write-OK "venv Python: $venvVer"
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 4 — Packages
# ─────────────────────────────────────────────────────────────────────────────

function Assert-Packages {
    Write-Section 'Python Packages'

    # Canary import — if streamlit is importable the full install is present.
    $null = & $VENV_PYTHON -c "import $CANARY_PACKAGE" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $slVer = & $VENV_PYTHON -c "import streamlit; print(streamlit.__version__)" 2>&1
        Write-OK "Packages present. streamlit $slVer"
        Write-Info "To reinstall: .venv\Scripts\pip install -e '.[dev]'"
        return
    }

    Write-Step "Package '$CANARY_PACKAGE' not found. Installing from pyproject.toml ..."
    Write-Step 'Upgrading pip ...'
    & $VENV_PYTHON -m pip install --upgrade pip --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Warn 'pip upgrade failed (non-fatal); continuing.'
    }

    Write-Step 'Running: pip install -e .[dev]  (this may take a few minutes on first run)'
    & $VENV_PYTHON -m pip install -e ".[dev]"
    if ($LASTEXITCODE -ne 0) {
        Write-Fail 'pip install failed.'
        Write-Info 'Check your internet connection and the contents of pyproject.toml.'
        Exit-WithPause
    }

    # Verify canary again
    $null = & $VENV_PYTHON -c "import $CANARY_PACKAGE" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Installation completed but '$CANARY_PACKAGE' still cannot be imported."
        Exit-WithPause
    }

    Write-OK 'All packages installed successfully.'
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 5 — Ollama (LLM backend)
# ─────────────────────────────────────────────────────────────────────────────

function Assert-Ollama {
    Write-Section 'Ollama  (LLM backend — http://localhost:11434)'

    if (Test-UrlReachable $OLLAMA_TAGS_URL) {
        Write-OK 'Ollama is running.'
        _Show-OllamaModels
        return
    }

    Write-Warn 'Ollama is not responding. Attempting to start it ...'

    if (-not (Get-Command 'ollama' -ErrorAction SilentlyContinue)) {
        Write-Fail '"ollama" not found in PATH.'
        Write-Info  'Download and install Ollama: https://ollama.com/download'
        Write-Info  'After installing, pull a model:  ollama pull llama3.2'
        Write-Warn  'The app will open, but LLM features will be disabled.'
        return
    }

    # Start ollama serve in a minimised background window
    Start-Process -FilePath 'ollama' `
                  -ArgumentList 'serve' `
                  -WindowStyle Minimized `
                  -ErrorAction SilentlyContinue

    Write-Step "Waiting up to ${OLLAMA_START_WAIT}s for Ollama to become ready ..."
    $elapsed = 0
    while ($elapsed -lt $OLLAMA_START_WAIT) {
        Start-Sleep -Seconds 1
        $elapsed++
        if (Test-UrlReachable $OLLAMA_TAGS_URL) {
            Write-OK "Ollama started (${elapsed}s)."
            _Show-OllamaModels
            return
        }
    }

    Write-Warn "Ollama did not respond within ${OLLAMA_START_WAIT}s."
    Write-Info  'LLM features will be unavailable until Ollama is running.'
    Write-Info  'Start manually in a separate terminal:  ollama serve'
}

function _Show-OllamaModels {
    try {
        $json   = Invoke-RestMethod -Uri $OLLAMA_TAGS_URL -TimeoutSec 3
        $models = $json.models | ForEach-Object { $_.name }
        if ($models.Count -gt 0) {
            Write-OK "Available models: $($models -join '  |  ')"
        } else {
            Write-Warn 'No local models found.'
            Write-Info  'Pull one with:  ollama pull llama3.2'
        }
    } catch {
        Write-Warn 'Could not list Ollama models (non-fatal).'
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 6 — Qdrant (vector DB — optional)
# ─────────────────────────────────────────────────────────────────────────────

function Test-Qdrant {
    Write-Section 'Qdrant  (vector DB — http://localhost:6333  — optional)'

    if (Test-UrlReachable $QDRANT_HEALTH_URL) {
        Write-OK 'Qdrant is running.'
    } else {
        Write-Warn 'Qdrant is not running.  RAG retrieval will be unavailable.'
        Write-Info  'Start it with:  docker compose up -d qdrant'
        Write-Info  'General-chat mode works without Qdrant.'
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# Step 7 — Launch Streamlit
# ─────────────────────────────────────────────────────────────────────────────

function Start-App {
    Write-Section 'Launching Application'

    if (-not (Test-Path $APP_ENTRY)) {
        Write-Fail "App entry point not found: $APP_ENTRY"
        Exit-WithPause
    }

    Write-OK  'Starting Streamlit ...'
    Write-Info 'URL: http://localhost:8501'
    Write-Info 'Network URL (LAN): Streamlit will print it below.'
    Write-Host ''
    Write-Host '  Press Ctrl+C in this window to stop the application.' `
        -ForegroundColor DarkGray
    Write-Host ''

    Set-Location $REPO_ROOT

    if (Test-Path $VENV_STREAMLIT) {
        & $VENV_STREAMLIT run $APP_ENTRY --server.headless $false
    } else {
        # Fallback: invoke as a module (always available when streamlit is installed)
        & $VENV_PYTHON -m streamlit run $APP_ENTRY --server.headless $false
    }

    # If we reach here, streamlit exited
    Write-Host ''
    Write-Host '  Application stopped.' -ForegroundColor DarkGray
    Write-Host '  Press any key to close this window ...' -ForegroundColor DarkGray
    try { $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown') } catch {}
}

# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

Write-Banner
Set-RepoRoot
$pythonExe = Assert-PythonVersion
Assert-Venv     $pythonExe
Assert-Packages
Assert-Ollama
Test-Qdrant

Write-Host ''
Write-Host $BAR -ForegroundColor DarkCyan
Write-Host '  All checks passed. Launching ...' -ForegroundColor Green
Write-Host $BAR -ForegroundColor DarkCyan

Start-App
