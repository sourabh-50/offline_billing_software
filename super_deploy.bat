@echo off
setlocal enabledelayedexpansion

echo ==================================================
echo   MASTER CLIENT DEPLOYER - ScaleAd
echo ==================================================

:: 1. Get User Input
set /p CLIENT_FOLDER="1. Enter Client Folder Name (e.g. omsai): "
set /p FULL_APP_NAME="2. Enter Full App Name (e.g. Omsai Billing Software): "
set /p SIDEBAR_TITLE="3. Enter Sidebar Title (e.g. ANUJ\nBILLING): "
set /p SHOP_DETAILS_NAME="4. Enter Shop Name for About Page (e.g. Anuj Mobile Shopee): "

if not exist "clients\%CLIENT_FOLDER%" (
    echo [ERROR] Folder 'clients\%CLIENT_FOLDER%' not found!
    pause
    exit /b 1
)

echo.
echo [1/5] Updating configuration for: %FULL_APP_NAME%...

:: Use PowerShell to update config.py
powershell -Command "(Get-Content config.py) -replace 'APP_NAME = \".*\"', 'APP_NAME = \"%FULL_APP_NAME%\"' | Set-Content config.py"
powershell -Command "(Get-Content config.py) -replace 'SIDEBAR_NAME = \".*\"', 'SIDEBAR_NAME = \"%SIDEBAR_TITLE%\"' | Set-Content config.py"
powershell -Command "(Get-Content config.py) -replace 'SHOP_NAME = \".*\"', 'SHOP_NAME = \"%SHOP_DETAILS_NAME%\"' | Set-Content config.py"

:: Use PowerShell to update the .spec file (for the .exe name)
powershell -Command "(Get-Content MobileShopBiller.spec) -replace 'name=''Premium Billing System''', 'name=''%FULL_APP_NAME%''' | Set-Content MobileShopBiller.spec"

:: Use PowerShell to update the Inno Setup script
powershell -Command "(Get-Content installer_script.iss) -replace 'AppName=.*', 'AppName=%FULL_APP_NAME%' | Set-Content installer_script.iss"
powershell -Command "(Get-Content installer_script.iss) -replace 'dist\\Client_Packages\\.*\\', 'dist\\Client_Packages\\%CLIENT_FOLDER%\\' | Set-Content installer_script.iss"
powershell -Command "(Get-Content installer_script.iss) -replace 'Premium Billing System', '%FULL_APP_NAME%' | Set-Content installer_script.iss"

echo [2/5] Preparing assets...
if exist "clients\%CLIENT_FOLDER%\header_img.png" copy /y "clients\%CLIENT_FOLDER%\header_img.png" "header_img.png"
if exist "clients\%CLIENT_FOLDER%\footer_img.png" copy /y "clients\%CLIENT_FOLDER%\footer_img.png" "footer_img.png"

echo [3/5] Cleaning old builds...
if exist build rmdir /s /q build

echo [4/5] Running PyInstaller (Creating the .exe)...
python -m PyInstaller --noconfirm MobileShopBiller.spec

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] PyInstaller failed!
    pause
    exit /b %ERRORLEVEL%
)

echo [5/5] Moving build to Client Package folder...
if not exist "dist\Client_Packages" mkdir "dist\Client_Packages"
if exist "dist\Client_Packages\%CLIENT_FOLDER%" rmdir /s /q "dist\Client_Packages\%CLIENT_FOLDER%"
mkdir "dist\Client_Packages\%CLIENT_FOLDER%"
move "dist\%FULL_APP_NAME%.exe" "dist\Client_Packages\%CLIENT_FOLDER%\"

echo.
echo ==================================================
echo   SUCCESS: %FULL_APP_NAME% is built!
echo   Location: dist\Client_Packages\%CLIENT_FOLDER%
echo.
echo   NEXT STEP: Open 'installer_script.iss' in Inno Setup 
echo   and click the PLAY button to create the Setup.exe.
echo ==================================================
pause
