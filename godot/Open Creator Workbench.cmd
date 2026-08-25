@echo off
setlocal
set "PROJECT=%~dp0"
set "GODOT=C:\tools\godot\godot.cmd"
if not exist "%GODOT%" (
    echo Godot was not found at %GODOT%
    pause
    exit /b 1
)
start "" "%GODOT%" --path "%PROJECT%"
