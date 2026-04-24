@echo off
echo ==================================================
echo   Building Omsai Billing Software (v1.1.0)
echo   Optimized for Windows 7, 10, 11
echo ==================================================

echo [1/3] Cleaning up old build files...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

echo [2/3] Running PyInstaller...
python -m PyInstaller --noconfirm MobileShopBiller.spec

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed! Check the error messages above.
    pause
    exit /b %ERRORLEVEL%
)

echo [3/3] Build Complete!
echo The executable is located in: dist\Omsai Billing Software\
echo.
echo TIP: To target Windows 7, ensure you are using Python 3.8.
pause
