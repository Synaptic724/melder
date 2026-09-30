param(
    [Parameter(Mandatory = $true)]
    [string]$MelderOpsRoot
)

# Use the original checkout so pytest resolves the same Spectrum fixtures and package.
# This runner installs nothing and preserves the original red XML under its existing name.
$taskRoot = (Resolve-Path -LiteralPath $MelderOpsRoot).Path
$taskPython = Join-Path $taskRoot '.venv314\Scripts\python.exe'
$taskDiagnostic = Join-Path $taskRoot 'context_compass\artifacts\2026-09-30_toolbox_native_dispense\test_native_dependency_lookup.py'
$taskResult = Join-Path $taskRoot 'context_compass\artifacts\2026-09-30_toolbox_native_dispense\native_dependency_lookup_recheck.xml'
if (-not (Test-Path -LiteralPath $taskPython -PathType Leaf)) {
    throw 'The original .venv314 interpreter is missing. Establish and record the runtime before reproducing.'
}
if (-not (Test-Path -LiteralPath $taskDiagnostic -PathType Leaf)) {
    throw 'The original diagnostic is missing. Restore the bundled diagnostic at this path in the MelderOps checkout.'
}
$taskPreviousPythonPath = $env:PYTHONPATH
$taskExitCode = 1
Push-Location -LiteralPath $taskRoot
try {
    $env:PYTHONPATH = Join-Path $taskRoot 'src'
    & $taskPython -m pytest $taskDiagnostic -q --tb=short "--junitxml=$taskResult"
    $taskExitCode = $LASTEXITCODE
}
finally {
    $env:PYTHONPATH = $taskPreviousPythonPath
    Pop-Location
}
exit $taskExitCode
