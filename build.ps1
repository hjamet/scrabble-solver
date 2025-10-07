# PowerShell script to build the Scrabble Solver project
# This script configures the MSVC environment and runs CMake build

param(
    [string]$Config = "Release",
    [switch]$Clean = $false
)

# Define the path to Visual Studio Build Tools environment script
$VsDevCmdPath = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat"

# Check if VsDevCmd.bat exists
if (-not (Test-Path $VsDevCmdPath)) {
    Write-Error "Visual Studio Build Tools not found at: $VsDevCmdPath"
    Write-Error "Please install Visual Studio Build Tools 2022 with C++ development workload"
    exit 1
}

Write-Host "Configuring MSVC environment..." -ForegroundColor Green

# Configure the MSVC environment by calling VsDevCmd.bat
# We need to use cmd.exe to execute the batch file and then run our commands
$buildScript = @"
@echo off
call "$VsDevCmdPath"
if errorlevel 1 (
    echo Failed to configure MSVC environment
    exit /b 1
)

echo MSVC environment configured successfully
echo.

REM Clean build directory if requested
if "$Clean"=="true" (
    echo Cleaning build directory...
    if exist build rmdir /s /q build
)

REM Create build directory if it doesn't exist
if not exist build mkdir build

REM Configure CMake with vcpkg toolchain (if available)
echo Configuring CMake...
if exist vcpkg (
    echo Using vcpkg toolchain for dependencies...
    cmake -B build -DCMAKE_BUILD_TYPE=$Config -DCMAKE_TOOLCHAIN_FILE=%CD%/vcpkg/scripts/buildsystems/vcpkg.cmake
) else (
    echo Using system dependencies...
    cmake -B build -DCMAKE_BUILD_TYPE=$Config
)
if errorlevel 1 (
    echo CMake configuration failed
    exit /b 1
)

REM Build the project
echo Building project...
cmake --build build --config $Config
if errorlevel 1 (
    echo Build failed
    exit /b 1
)

echo.
echo Build completed successfully!
echo Executable location: build\$Config\test_main.exe

REM Run tests if requested
echo.
echo Running tests...
cd build
ctest --output-on-failure
cd ..
"@

# Write the temporary batch script
$tempScript = "temp_build.bat"
$buildScript | Out-File -FilePath $tempScript -Encoding ASCII

try {
    # Execute the batch script
    Write-Host "Starting build process..." -ForegroundColor Green
    & cmd.exe /c $tempScript
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nBuild completed successfully!" -ForegroundColor Green
        Write-Host "Test executable: build\$Config\test_main.exe" -ForegroundColor Cyan
    }
    else {
        Write-Error "Build failed with exit code: $LASTEXITCODE"
        exit $LASTEXITCODE
    }
}
finally {
    # Clean up temporary script
    if (Test-Path $tempScript) {
        Remove-Item $tempScript
    }
}
