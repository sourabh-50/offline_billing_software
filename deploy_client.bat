@echo off
setlocal enabledelayedexpansion

echo ==================================================
echo   Premium Billing System - Client Deployer
echo   ScaleAd Digital Growth Agency
echo ==================================================

if "%~1"=="" (
    set /p CLIENT_NAME="Enter Client Name (e.g. omsai): "
) else (
    set CLIENT_NAME=%~1
)

if not exist "clients\%CLIENT_NAME%" (
    echo [ERROR] Client folder 'clients\%CLIENT_NAME%' not found!
    pause
    exit /b 1
)

echo.
echo [1/4] Preparing assets for %CLIENT_NAME%...
if exist "clients\%CLIENT_NAME%\header_img.png" (
    copy /y "clients\%CLIENT_NAME%\header_img.png" "header_img.png"
)
if exist "clients\%CLIENT_NAME%\footer_img.png" (
    copy /y "clients\%CLIENT_NAME%\footer_img.png" "footer_img.png"
)

echo [2/4] Cleaning previous builds...
if exist build rmdir /s /q build

echo [3/4] Building application...
python -m PyInstaller --noconfirm MobileShopBiller.spec

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed for %CLIENT_NAME%.
    pause
    exit /b %ERRORLEVEL%
)

echo [4/4] Organizing final package...
if not exist "dist\Client_Packages" mkdir "dist\Client_Packages"
if exist "dist\Client_Packages\%CLIENT_NAME%" rmdir /s /q "dist\Client_Packages\%CLIENT_NAME%"

move "dist\Premium Billing System" "dist\Client_Packages\%CLIENT_NAME%"

echo.
echo ==================================================
echo   DEPLOYMENT COMPLETE!
echo   Target: dist\Client_Packages\%CLIENT_NAME%
echo ==================================================
pause
