@echo off
setlocal
set "ROOT=%~dp0"
set "FREECADCMD=%LOCALAPPDATA%\Programs\FreeCAD 1.1\bin\freecadcmd.exe"
set "GODOT=C:\tools\godot\godot.cmd"

echo Verifying FreeCAD models and exports...
"%FREECADCMD%" "%ROOT%freecad\src\verify_creator_shapes.py"
if errorlevel 1 goto :failed

echo Importing and verifying the Godot workbench...
"%GODOT%" --headless --path "%ROOT%godot" --import
if errorlevel 1 goto :failed
"%GODOT%" --headless --path "%ROOT%godot" --script res://scripts/verify_project.gd
if errorlevel 1 goto :failed

echo.
echo CREATOR_KIT_ALL_CHECKS_OK
pause
exit /b 0

:failed
echo.
echo CREATOR_KIT_CHECK_FAILED
pause
exit /b 1
