# PowerShell script to install Google Test on Windows
# This script uses vcpkg to install Google Test

Write-Host "Installing Google Test using vcpkg..." -ForegroundColor Green

# Check if vcpkg is installed
if (-not (Get-Command vcpkg -ErrorAction SilentlyContinue)) {
    Write-Host "vcpkg not found. Installing vcpkg..." -ForegroundColor Yellow
    
    # Clone vcpkg
    git clone https://github.com/Microsoft/vcpkg.git
    cd vcpkg
    
    # Bootstrap vcpkg
    .\bootstrap-vcpkg.bat
    
    # Add to PATH for current session
    $env:PATH += ";$PWD"
    
    cd ..
}

# Install Google Test
Write-Host "Installing Google Test..." -ForegroundColor Green
vcpkg install gtest:x64-windows

# Create a vcpkg-configuration.json file for CMake integration
$vcpkgConfig = @"
{
    "default-registry": {
        "kind": "git",
        "repository": "https://github.com/Microsoft/vcpkg.git",
        "baseline": "latest"
    },
    "registries": []
}
"@

$vcpkgConfig | Out-File -FilePath "vcpkg-configuration.json" -Encoding UTF8

Write-Host "Google Test installation completed!" -ForegroundColor Green
Write-Host "You can now configure your project with CMake using:" -ForegroundColor Cyan
Write-Host "cmake -B build -DCMAKE_TOOLCHAIN_FILE=[vcpkg root]/scripts/buildsystems/vcpkg.cmake" -ForegroundColor Cyan
