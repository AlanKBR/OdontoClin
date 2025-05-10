# PowerShell script to run linting
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$scriptPath\lint.py" @args
