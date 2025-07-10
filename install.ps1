# Change to the directory where the script is located
Set-Location -Path $PSScriptRoot

# Check if Python is installed
try {
    Write-Host "Checking for Python installation..."
    python --version
} catch {
    Write-Host "Python not found. Please install Python 3.8+ from https://www.python.org/downloads/ and try again."
    exit 1
}

# Check if pip is installed
try {
    Write-Host "Checking for pip installation..."
    pip --version
} catch {
    Write-Host "pip not found. Please ensure pip is installed and in your PATH."
    exit 1
}

# Install required Python packages
Write-Host "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

# Run the application
Write-Host "Starting the English Enhancer application..."
python english_enhancer.py