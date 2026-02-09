@echo off
echo Starting ngrok for Flask app...
echo.
echo Make sure you've:
echo 1. Downloaded ngrok from https://ngrok.com/download
echo 2. Extracted it to a folder (e.g., C:\ngrok)
echo 3. Updated the path below to match your ngrok location
echo.
pause

REM Update this path to where you extracted ngrok
set NGROK_PATH=C:\ngrok\ngrok.exe

if not exist "%NGROK_PATH%" (
    echo ERROR: ngrok.exe not found at %NGROK_PATH%
    echo Please update the NGROK_PATH in this file to point to your ngrok.exe
    pause
    exit
)

echo Starting ngrok on port 5000...
"%NGROK_PATH%" http 5000

pause









