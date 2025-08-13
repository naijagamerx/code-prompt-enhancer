# Clean the console and show a startup message
Clear-Host
Write-Host "Starting Optimized Coding English Enhancer..."

# Define the repository URL and local directory
$repoUrl = "https://raw.githubusercontent.com/naijagamerx/code-prompt-enhancer/refactor/pyqt-rewrite"
$installDir = "$env:APPDATA\code-prompt-enhancer"

# Create the installation directory if it doesn't exist
if (-not (Test-Path -Path $installDir)) {
    New-Item -Path $installDir -ItemType Directory | Out-Null
}

# Define the files to download
$files = @(
    "ascii_art.txt",
    "encrypt_config.py",
    "prompt_enhancer.py",
    "qt_main_window.py",
    "requirements.txt"
)

# Download each file
foreach ($file in $files) {
    $source = "$repoUrl/$file"
    $destination = "$installDir\$file"
    try {
        Invoke-RestMethod -Uri $source -OutFile $destination -ErrorAction SilentlyContinue
    } catch {
        Write-Error "Failed to download $file from $source. Error: $_"
        exit 1
    }
}

# Navigate to the installation directory and start the application
Push-Location $installDir
# Ensure requirements are installed silently
pip install -r requirements.txt --quiet
# Execute the python GUI script without a console window
Start-Process pythonw -ArgumentList "prompt_enhancer.py"
Pop-Location