# Define the repository URL and local directory
$repoUrl = "https://raw.githubusercontent.com/naijagamerx/code-prompt-enhancer/main"
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
    "requirements.txt",
    "start.bat"
)

# Download each file
foreach ($file in $files) {
    $source = "$repoUrl/$file"
    $destination = "$installDir\$file"
    try {
        Invoke-RestMethod -Uri $source -OutFile $destination
        Write-Host "Successfully downloaded $file"
    } catch {
        Write-Error "Failed to download $file from $source. Error: $_"
        exit 1
    }
}

# Navigate to the installation directory and start the application
Push-Location $installDir
# Ensure requirements are installed
pip install -r requirements.txt
# Execute the start batch file
cmd /c start.bat
Pop-Location

Write-Host "Application setup complete and started."