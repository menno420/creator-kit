@echo off
setlocal
set "FREECAD=%LOCALAPPDATA%\Programs\FreeCAD 1.1\bin\freecad.exe"
set "MODEL=%~dp0cad\creator-shapes.FCStd"
if not exist "%MODEL%" (
    echo The library has not been built yet. Run "Rebuild FreeCAD Library.cmd" first.
    pause
    exit /b 1
)
start "" "%FREECAD%" "%MODEL%"
