# PowerShell Installation Script for Coding English Enhancer
# This script downloads and runs the Coding English Enhancer application

# Set execution policy for current process
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force

# Clear screen and show ASCII art
Clear-Host
Write-Host ""
Write-Host " ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ████████╗███████╗██████╗ " -ForegroundColor Cyan
Write-Host " ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝██╔════╝██╔══██╗" -ForegroundColor Cyan
Write-Host " ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝   ██║   █████╗  ██████╔╝" -ForegroundColor Cyan
Write-Host " ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝    ██║   ██╔══╝  ██╔══██╗" -ForegroundColor Cyan
Write-Host " ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║        ██║   ███████╗██║  ██║" -ForegroundColor Cyan
Write-Host " ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝        ╚═╝   ╚══════╝╚═╝  ╚═╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Coding English Enhancer v1.0 - Installation Script" -ForegroundColor Green
Write-Host "App by demohomex" -ForegroundColor Yellow
Write-Host ""

# Configuration
$AppName = "Coding English Enhancer"
$AppUrl = "https://raw.githubusercontent.com/naijagamerx/code-prompt-enhancer/main/prompt_enhancer.py"
$LocalPath = "$env:TEMP\prompt_enhancer.py"
$RequirementsUrl = "https://raw.githubusercontent.com/naijagamerx/code-prompt-enhancer/main/requirements.txt"
$RequirementsPath = "$env:TEMP\requirements.txt"

# Function to check if Python is installed
function Test-PythonInstalled {
    try {
        $pythonVersion = python --version 2>&1
        if ($pythonVersion -match "Python \d+\.\d+\.\d+") {
            Write-Host "✓ Python is installed: $pythonVersion" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "✗ Python is not installed or not in PATH" -ForegroundColor Red
        return $false
    }
    return $false
}

# Function to check if pip is available
function Test-PipInstalled {
    try {
        $pipVersion = pip --version 2>&1
        if ($pipVersion -match "pip \d+\.\d+") {
            Write-Host "✓ pip is available: $pipVersion" -ForegroundColor Green
            return $true
        }
    }
    catch {
        Write-Host "✗ pip is not available" -ForegroundColor Red
        return $false
    }
    return $false
}

# Function to download file
function Download-File {
    param(
        [string]$Url,
        [string]$OutputPath,
        [string]$Description
    )
    
    try {
        Write-Host "Downloading $Description..." -ForegroundColor Yellow
        Invoke-RestMethod -Uri $Url -OutFile $OutputPath -ErrorAction Stop
        Write-Host "✓ $Description downloaded successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ Failed to download $Description" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Function to install Python packages
function Install-Requirements {
    param([string]$RequirementsPath)
    
    if (-not (Test-Path $RequirementsPath)) {
        Write-Host "✗ Requirements file not found" -ForegroundColor Red
        return $false
    }
    
    try {
        Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
        pip install -r $RequirementsPath --quiet
        Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        return $false
    }
}

# Main installation process
try {
    Write-Host "Starting installation process..." -ForegroundColor Cyan
    Write-Host ""
    
    # Check prerequisites
    if (-not (Test-PythonInstalled)) {
        Write-Host ""
        Write-Host "Please install Python first:" -ForegroundColor Yellow
        Write-Host "1. Go to https://python.org/downloads" -ForegroundColor White
        Write-Host "2. Download and install Python (make sure to check 'Add Python to PATH')" -ForegroundColor White
        Write-Host "3. Restart PowerShell and run this script again" -ForegroundColor White
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    if (-not (Test-PipInstalled)) {
        Write-Host ""
        Write-Host "pip is required but not available. Please reinstall Python with pip included." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host ""
    
    # Download the main application
    if (-not (Download-File -Url $AppUrl -OutputPath $LocalPath -Description "main application")) {
        throw "Failed to download the main application"
    }
    
    # Download requirements
    if (-not (Download-File -Url $RequirementsUrl -OutputPath $RequirementsPath -Description "requirements file")) {
        Write-Host "Warning: Could not download requirements file. Attempting to install dependencies manually..." -ForegroundColor Yellow
        
        # Fallback: install known dependencies
        $dependencies = @("pyperclip", "keyboard", "cryptography", "groq", "ttkthemes")
        Write-Host "Installing dependencies: $($dependencies -join ', ')" -ForegroundColor Yellow
        
        foreach ($dep in $dependencies) {
            try {
                pip install $dep --quiet
                Write-Host "✓ Installed $dep" -ForegroundColor Green
            }
            catch {
                Write-Host "✗ Failed to install $dep" -ForegroundColor Red
            }
        }
    }
    else {
        # Install from requirements file
        if (-not (Install-Requirements -RequirementsPath $RequirementsPath)) {
            throw "Failed to install dependencies"
        }
    }
    
    Write-Host ""
    Write-Host "✓ Installation completed successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Ask user if they want to run the application now
    $runNow = Read-Host "Would you like to start the application now? (y/n)"
    
    if ($runNow -match "^[Yy]") {
        Write-Host ""
        Write-Host "Starting $AppName..." -ForegroundColor Cyan
        Write-Host "Note: The application will start in a new window." -ForegroundColor Yellow
        Write-Host ""
        
        # Start the application
        Start-Process python -ArgumentList "`"$LocalPath`"" -NoNewWindow
        
        Write-Host "✓ Application started!" -ForegroundColor Green
        Write-Host ""
        Write-Host "The application is now running. You can:" -ForegroundColor White
        Write-Host "• Use the GUI interface that just opened" -ForegroundColor White
        Write-Host "• Use global hotkeys (Ctrl+Shift+E or Ctrl+Shift+R) from anywhere" -ForegroundColor White
        Write-Host "• Copy text and press the hotkey to enhance it automatically" -ForegroundColor White
    }
    else {
        Write-Host ""
        Write-Host "You can run the application later with:" -ForegroundColor White
        Write-Host "python `"$LocalPath`"" -ForegroundColor Cyan
    }
    
    Write-Host ""
    Write-Host "Installation location: $LocalPath" -ForegroundColor Gray
    Write-Host ""
}
catch {
    Write-Host ""
    Write-Host "✗ Installation failed!" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please try the following:" -ForegroundColor Yellow
    Write-Host "1. Make sure you have an internet connection" -ForegroundColor White
    Write-Host "2. Run PowerShell as Administrator" -ForegroundColor White
    Write-Host "3. Check if the download URLs are accessible" -ForegroundColor White
    Write-Host ""
}
finally {
    # Cleanup temporary files
    if (Test-Path $RequirementsPath) {
        Remove-Item $RequirementsPath -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host "Press Enter to exit..." -ForegroundColor Gray
    Read-Host
}
