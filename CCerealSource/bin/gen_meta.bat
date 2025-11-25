@echo off
echo Generating Serialization Metadata...

SET TOOL_PATH=../tools/meta_generator.py

SET DEFAULT_SOURCE=src\General\Headers*.h


IF "%~1"=="" (
echo No input files specified. Scanning default directory...
SET INPUT_FILES="%DEFAULT_SOURCE%"
) ELSE (

echo Input arguments detected.
SET INPUT_FILES=%*
)


python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
echo Error: Python is not installed or not in PATH.
pause
exit /b
)


python "%TOOL_PATH%" %INPUT_FILES%

echo.
if %ERRORLEVEL% EQU 0 (
echo [SUCCESS] Metadata generation complete.
) else (
echo [ERROR] Script failed.
)

pause