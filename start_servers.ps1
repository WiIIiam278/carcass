# Starts all servers specified
Param(
    [string]$directory = "./servers/"
)

# Find all start.bat files in the directory
$files = Get-ChildItem $directory  -Recurse -File -Filter "start.ps1"

# Start each server
foreach ($file in $files) {
    Powershell -executionpolicy remotesigned -File  $file
}

Exit 0