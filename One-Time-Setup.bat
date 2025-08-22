@echo off
setlocal EnableDelayedExpansion
echo ==============================
echo        YTDM Setup
echo ==============================

:: ----------------------------------
:: 1. Base folder (where script is)
:: ----------------------------------
set "BASE_DIR=%~dp0"
if "%BASE_DIR:~-1%"=="\" set "BASE_DIR=%BASE_DIR:~0,-1%"

:: ----------------------------------
:: 2. Update PATH: remove old YTDM bin, add current bin
:: ----------------------------------
echo Updating PATH...
for /f "tokens=2*" %%A in ('reg query "HKCU\Environment" /v PATH 2^>nul') do set "CUR_PATH=%%B"

:: Remove any old YTDM bin paths
set "NEW_PATH="
for %%P in ("!CUR_PATH:;=";"!") do (
    echo %%~P | find /i "\YTDM App\bin" >nul
    if errorlevel 1 (
        if defined NEW_PATH (
            set "NEW_PATH=!NEW_PATH!;%%~P"
        ) else (
            set "NEW_PATH=%%~P"
        )
    )
)

:: Add current bin folder
set "BIN_DIR=%BASE_DIR%\bin"
if defined NEW_PATH (
    set "NEW_PATH=!NEW_PATH!;%BIN_DIR%"
) else (
    set "NEW_PATH=%BIN_DIR%"
)

:: Apply updated PATH
setx PATH "%NEW_PATH%"
echo PATH updated successfully.
echo.

:: ----------------------------------
:: 3. Install Python dependencies
:: ----------------------------------
echo Installing Python dependencies...
where py >nul 2>nul
if %errorlevel%==0 (
    py -m pip install --upgrade pip
    py -m pip install PyQt5 PyQt5-tools 
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        python -m pip install --upgrade pip
        python -m pip install PyQt5 PyQt5-tools 
    ) else (
        echo ERROR: Python not found! Please install Python 3.13+ and re-run this installer.
        pause
        exit /b 1
    )
)
echo

echo ==================================================
echo      Setup Completed!
echo Please restart your computer to apply changes.
echo ==================================================
pause
