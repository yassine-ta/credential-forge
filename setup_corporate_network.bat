@echo off
REM CredentialForge Corporate Network Configuration for Windows
REM This script sets up environment variables for corporate networks

echo CredentialForge Corporate Network Setup
echo ========================================

echo.
echo This script will configure CredentialForge for corporate networks.
echo It will disable SSL verification and set trusted hosts.
echo.
echo WARNING: This reduces security but may be necessary in corporate environments.
echo.

set /p CONFIRM="Continue? (y/N): "
if /i not "%CONFIRM%"=="y" (
    echo Configuration cancelled.
    pause
    exit /b 1
)

echo.
echo Configuring environment variables...

REM Set SSL verification to false for corporate networks
setx CREDENTIALFORGE_SSL_VERIFY "false" >nul
echo - SSL verification disabled

REM Set trusted hosts
setx CREDENTIALFORGE_TRUSTED_HOSTS "huggingface.co,pypi.org,files.pythonhosted.org" >nul
echo - Trusted hosts configured

REM Check for existing proxy settings
if defined HTTP_PROXY (
    echo - HTTP proxy already configured: %HTTP_PROXY%
) else (
    set /p PROXY_URL="Enter HTTP proxy URL (or press Enter to skip): "
    if not "!PROXY_URL!"=="" (
        setx HTTP_PROXY "!PROXY_URL!" >nul
        setx HTTPS_PROXY "!PROXY_URL!" >nul
        echo - Proxy configured: !PROXY_URL!
    )
)

echo.
echo Configuration complete!
echo.
echo The following environment variables have been set:
echo - CREDENTIALFORGE_SSL_VERIFY=false
echo - CREDENTIALFORGE_TRUSTED_HOSTS=huggingface.co,pypi.org,files.pythonhosted.org
echo.
echo NOTE: You may need to restart your terminal or IDE for changes to take effect.
echo.

REM Test network connectivity
echo Testing network connectivity...
python setup_corporate_network.py 2>nul
if errorlevel 1 (
    echo.
    echo To manually test network configuration, run:
    echo   python setup_corporate_network.py
)

echo.
echo Setup complete! You can now try downloading models again.
pause
