@echo off

echo Creating executable...
pyinstaller --onefile --windowed main.py
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create executable
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo Your executable is located in the 'dist' folder
echo.
pause 