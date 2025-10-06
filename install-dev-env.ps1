# C Development Environment Installation Script for Windows
# Must be run as administrator

param(
    [switch]$SkipMSYS2Install
)

Write-Host "=== C Development Environment Installation ===" -ForegroundColor Green
Write-Host ""

# Check administrator privileges
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERROR: This script must be run as administrator" -ForegroundColor Red
    Write-Host "Right-click PowerShell -> 'Run as administrator'" -ForegroundColor Yellow
    exit 1
}

$msys2Path = "C:\msys64"
$msys2BinPath = "$msys2Path\ucrt64\bin"

# Step 1: MSYS2 Installation
if (-not $SkipMSYS2Install) {
    Write-Host "=== Step 1: MSYS2 Installation ===" -ForegroundColor Cyan
    
    if (Test-Path $msys2Path) {
        Write-Host "MSYS2 is already installed in $msys2Path" -ForegroundColor Yellow
    } else {
        Write-Host "Downloading and installing MSYS2..." -ForegroundColor White
        $msys2Installer = "$env:TEMP\msys2-installer.exe"
        
        try {
            Invoke-WebRequest -Uri "https://github.com/msys2/msys2-installer/releases/latest/download/msys2-x86_64-latest.exe" -OutFile $msys2Installer
            Start-Process -FilePath $msys2Installer -ArgumentList "in" -Wait
            Remove-Item $msys2Installer -Force
            Write-Host "✅ MSYS2 installed successfully" -ForegroundColor Green
        } catch {
            Write-Host "❌ Error installing MSYS2: $($_.Exception.Message)" -ForegroundColor Red
            Write-Host "Install MSYS2 manually from https://www.msys2.org/" -ForegroundColor Yellow
            exit 1
        }
    }
}

# Step 2: MSYS2 Installation Verification
Write-Host ""
Write-Host "=== Step 2: MSYS2 Installation Verification ===" -ForegroundColor Cyan

if (-not (Test-Path $msys2Path)) {
    Write-Host "❌ MSYS2 is not installed in $msys2Path" -ForegroundColor Red
    Write-Host "Install MSYS2 manually from https://www.msys2.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ MSYS2 detected in: $msys2Path" -ForegroundColor Green

# Step 3: Development Tools Installation
Write-Host ""
Write-Host "=== Step 3: Development Tools Installation ===" -ForegroundColor Cyan
Write-Host "This step must be performed in the MSYS2 UCRT64 terminal" -ForegroundColor Yellow
Write-Host ""

$installScript = @"
#!/bin/bash
echo "=== C Development Tools Installation ==="
echo ""

# System update
echo "Updating package manager..."
pacman -Syu --noconfirm
pacman -Su --noconfirm

# Install base tools
echo "Installing compilation toolchain..."
pacman -S --needed --noconfirm base-devel mingw-w64-ucrt-x86_64-toolchain

# Install CMake
echo "Installing CMake..."
pacman -S --needed --noconfirm mingw-w64-ucrt-x86_64-cmake

# Install additional tools
echo "Installing additional tools..."
pacman -S --needed --noconfirm \
    mingw-w64-ucrt-x86_64-gdb \
    mingw-w64-ucrt-x86_64-git \
    mingw-w64-ucrt-x86_64-pkg-config \
    mingw-w64-ucrt-x86_64-ninja

echo ""
echo "=== Installation completed ==="
echo "Version verification:"
gcc --version | head -1
make --version | head -1
cmake --version | head -1
gdb --version | head -1
"@

$installScript | Out-File -FilePath "install-tools.sh" -Encoding UTF8
Write-Host "✅ Installation script created: install-tools.sh" -ForegroundColor Green
Write-Host ""
Write-Host "Instructions:" -ForegroundColor Yellow
Write-Host "1. Launch 'MSYS2 UCRT64' from the Start Menu" -ForegroundColor White
Write-Host "2. Navigate to this directory: cd '$(Get-Location)'" -ForegroundColor White
Write-Host "3. Run the script: ./install-tools.sh" -ForegroundColor White
Write-Host ""

# Step 4: System PATH Update
Write-Host "=== Step 4: System PATH Update ===" -ForegroundColor Cyan

$currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")

if ($currentPath -like "*$msys2BinPath*") {
    Write-Host "MSYS2 is already in the system PATH" -ForegroundColor Yellow
} else {
    $newPath = $currentPath + ";" + $msys2BinPath
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "Machine")
    Write-Host "✅ MSYS2 added to system PATH" -ForegroundColor Green
}

# Final Summary
Write-Host ""
Write-Host "=== Installation completed ===" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Launch 'MSYS2 UCRT64' from the Start Menu" -ForegroundColor White
Write-Host "2. Navigate to this directory" -ForegroundColor White
Write-Host "3. Run: ./install-tools.sh" -ForegroundColor White
Write-Host "4. Restart your terminal (Git Bash or PowerShell)" -ForegroundColor White
Write-Host "5. Test with: gcc --version" -ForegroundColor White
Write-Host ""
Write-Host "Files created:" -ForegroundColor Cyan
Write-Host "- install-tools.sh (MSYS2 installation script)" -ForegroundColor White
