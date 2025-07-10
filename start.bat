@echo off
color 0A
chcp 65001 >nul
echo.
type ascii_art.txt
echo.
echo.
echo.
echo Welcome to Coding English Enhancer v1.0
echo App by demohomex
echo.
setlocal enabledelayedexpansion

set /a count=0
echo Please choose a Python script to run:
echo.

for %%f in (*.py) do (
    if /i not "%%f"=="test_enhancer.py" (
        set /a count+=1
        set "file[!count!]=%%f"
        echo !count!. %%f
    )
)

echo.
set /p choice="Enter the number of the script to run: "

if not defined file[%choice%] (
    echo Invalid choice.
    pause
    exit /b
)

py "!file[%choice%]!"

endlocal