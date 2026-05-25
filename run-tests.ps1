<#
.SYNOPSIS
    Runs the ncr-legal-assist-ai test suite and displays a formatted report.

.DESCRIPTION
    Locates the virtual-environment Python, executes pytest with verbose output,
    then renders a grouped result table (by file) plus an overall summary.

.PARAMETER VenvPath
    Path to the virtual environment root.  Default: .venv

.PARAMETER Filter
    Optional pytest -k expression to run a subset of tests.
    Example: -Filter "test_verifier"

.PARAMETER File
    Optional path (or glob) to run a single test file.
    Example: -File "tests/test_chunker.py"

.PARAMETER Coverage
    Emit a coverage report (requires pytest-cov: pip install pytest-cov).

.EXAMPLE
    .\run-tests.ps1

.EXAMPLE
    .\run-tests.ps1 -Filter "test_chunker"

.EXAMPLE
    .\run-tests.ps1 -File "tests/test_verifier.py" -Coverage
#>

[CmdletBinding()]
param(
    [string] $VenvPath = ".venv",
    [string] $Filter   = "",
    [string] $File     = "",
    [switch] $Coverage
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ── Colour helpers ────────────────────────────────────────────────────────────

function Write-Color {
    param([string]$Text, [ConsoleColor]$Color = "White", [switch]$NoNewline)
    if ($NoNewline) {
        Write-Host $Text -ForegroundColor $Color -NoNewline
    } else {
        Write-Host $Text -ForegroundColor $Color
    }
}

function Write-Banner {
    param([string]$Title)
    $inner  = "  $Title  "
    $border = "─" * $inner.Length
    Write-Host ""
    Write-Color "  ┌$border┐" Cyan
    Write-Color "  │$inner│" Cyan
    Write-Color "  └$border┘" Cyan
    Write-Host ""
}

function Write-Section {
    param([string]$Title)
    $pad = "─" * [Math]::Max(0, 62 - $Title.Length)
    Write-Host ""
    Write-Color "  ┌─ $Title $pad" DarkCyan
}

function Get-StatusIcon { param([string]$s)
    switch ($s) {
        "PASSED"  { return "✓" } "FAILED"  { return "✗" }
        "ERROR"   { return "!" } "SKIPPED" { return "○" }
        "XFAIL"   { return "x" } "XPASS"   { return "?" }
        default   { return "·" }
    }
}

function Get-StatusColor { param([string]$s)
    switch ($s) {
        "PASSED"  { return [ConsoleColor]"Green"      }
        "FAILED"  { return [ConsoleColor]"Red"        }
        "ERROR"   { return [ConsoleColor]"Red"        }
        "SKIPPED" { return [ConsoleColor]"Yellow"     }
        "XFAIL"   { return [ConsoleColor]"DarkYellow" }
        "XPASS"   { return [ConsoleColor]"Cyan"       }
        default   { return [ConsoleColor]"Gray"       }
    }
}

# ── Locate Python ─────────────────────────────────────────────────────────────

function Get-PythonExe { param([string]$Root)
    foreach ($c in @("$Root\Scripts\python.exe", "$Root/bin/python")) {
        if (Test-Path $c) { return $c }
    }
    return $null
}

Write-Banner "ncr-legal-assist-ai · Test Suite"

$pythonExe = Get-PythonExe -Root $VenvPath
if (-not $pythonExe) {
    Write-Color "  ERROR: No Python found in '$VenvPath'." Red
    Write-Color "  Run:   python -m venv $VenvPath" Yellow
    Write-Color "         $VenvPath\Scripts\pip install -e '.[dev]'" Yellow
    exit 1
}

$pyVersion = (& $pythonExe --version 2>&1).ToString().Trim()
Write-Color "  Python   : $pyVersion" Gray
Write-Color "  Venv     : $VenvPath" Gray
Write-Color "  Directory: $PWD" Gray

# ── Build pytest argument list ────────────────────────────────────────────────

$pytestArgs = [System.Collections.Generic.List[string]]::new()
$pytestArgs.AddRange([string[]]@("-m", "pytest", "--tb=short", "-v", "--no-header", "--color=no"))

if ($File)   { $pytestArgs.Add($File);         Write-Color "  Scope    : $File"   Gray }
else         { $pytestArgs.Add("tests") }

if ($Filter) { $pytestArgs.AddRange([string[]]@("-k", $Filter)); Write-Color "  Filter   : $Filter" Gray }
if ($Coverage) {
    $pytestArgs.AddRange([string[]]@("--cov=src", "--cov-report=term-missing"))
    Write-Color "  Coverage : enabled" Gray
}

Write-Host ""

# ── Run tests ─────────────────────────────────────────────────────────────────

Write-Section "Running tests"
Write-Host ""

$startTime = Get-Date
$rawLines  = [System.Collections.Generic.List[string]]::new()

& $pythonExe @pytestArgs 2>&1 | ForEach-Object {
    $line = $_.ToString()
    $rawLines.Add($line)
    Write-Host "    $line"
}

$exitCode = $LASTEXITCODE
$elapsed  = (Get-Date) - $startTime

# ── Parse results ─────────────────────────────────────────────────────────────
# pytest -v lines look like:
#   tests/test_verifier.py::ClassName::method_name PASSED   [ 50%]
#   tests/test_verifier.py::function_name          FAILED   [ 75%]

$resultRx = '^(tests[\\/][^\s:]+\.py)::(.+?)\s+(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)\s*'
$results  = [System.Collections.Generic.List[PSCustomObject]]::new()

foreach ($line in $rawLines) {
    if ($line -match $resultRx) {
        $filePart   = $Matches[1] -replace '\\', '/'
        $testPart   = $Matches[2].Trim()
        $statusPart = $Matches[3].Trim()

        if ($testPart -match '^(.+)::(.+)$') {
            $class  = $Matches[1]
            $method = $Matches[2]
        } else {
            $class  = "(module)"
            $method = $testPart
        }

        $results.Add([PSCustomObject]@{
            File   = $filePart
            Class  = $class
            Method = $method
            Status = $statusPart
        })
    }
}

# ── Results table by file ─────────────────────────────────────────────────────

if ($results.Count -gt 0) {
    Write-Section "Results by file"
    Write-Host ""

    $grouped = $results | Group-Object -Property File | Sort-Object Name

    foreach ($grp in $grouped) {
        $pass    = @($grp.Group | Where-Object Status -eq "PASSED").Count
        $fail    = @($grp.Group | Where-Object { $_.Status -in @("FAILED","ERROR") }).Count
        $skipped = @($grp.Group | Where-Object Status -eq "SKIPPED").Count
        $total   = $grp.Count

        $fileColor = if ($fail -gt 0) { "Red" } else { "Green" }

        Write-Color "  $($grp.Name)" $fileColor -NoNewline
        Write-Color "  [$total]  " Gray -NoNewline
        Write-Color "$pass passed" Green -NoNewline
        if ($fail    -gt 0) { Write-Color "  $fail failed"   Red    -NoNewline }
        if ($skipped -gt 0) { Write-Color "  $skipped skipped" Yellow -NoNewline }
        Write-Host ""

        foreach ($r in $grp.Group) {
            $icon  = Get-StatusIcon  -s $r.Status
            $color = Get-StatusColor -s $r.Status
            $label = if ($r.Class -ne "(module)") { "$($r.Class)::$($r.Method)" } else { $r.Method }
            Write-Color ("    {0} {1}" -f $icon, $label) $color
        }
        Write-Host ""
    }
}

# ── Summary table ─────────────────────────────────────────────────────────────

Write-Section "Summary"
Write-Host ""

$totalPass    = @($results | Where-Object Status -eq "PASSED").Count
$totalFail    = @($results | Where-Object { $_.Status -in @("FAILED","ERROR") }).Count
$totalSkipped = @($results | Where-Object Status -eq "SKIPPED").Count
$totalCount   = $results.Count
$durSec       = [Math]::Round($elapsed.TotalSeconds, 2)

$col = 22
Write-Color ("  {0,-$col} {1}" -f "Metric", "Value") DarkGray
Write-Color ("  {0,-$col} {1}" -f ("─" * ($col - 1)), "──────") DarkGray

@(
    @{ M = "Total tests";    V = "$totalCount";    C = "White"  }
    @{ M = "Passed";         V = "$totalPass";     C = "Green"  }
    @{ M = "Failed / Error"; V = "$totalFail";     C = $(if ($totalFail -gt 0) { "Red" } else { "Green" }) }
    @{ M = "Skipped";        V = "$totalSkipped";  C = "Yellow" }
    @{ M = "Duration";       V = "${durSec}s";     C = "Gray"   }
) | ForEach-Object {
    Write-Color ("  {0,-$col}" -f $_["M"]) Gray -NoNewline
    Write-Color $_["V"] $_["C"]
}

Write-Host ""

# ── Final verdict ─────────────────────────────────────────────────────────────

if ($exitCode -eq 0) {
    Write-Color "  ✓  All tests passed." Green
} else {
    Write-Color "  ✗  One or more tests failed. See output above." Red
}

Write-Host ""
exit $exitCode
