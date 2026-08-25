@echo off
setlocal
set "KIT=%~dp0"
set "FREECADCMD=%LOCALAPPDATA%\Programs\FreeCAD 1.1\bin\freecadcmd.exe"

echo.
echo  Menno Creator Kit - rebuild FreeCAD library
echo  ============================================
echo.

if not exist "%FREECADCMD%" (
    echo  ERROR: FreeCAD was not found at:
    echo    %FREECADCMD%
    pause
    exit /b 1
)

"%SystemRoot%\System32\tasklist.exe" /FI "IMAGENAME eq FreeCAD.exe" 2^>nul | "%SystemRoot%\System32\find.exe" /I "FreeCAD.exe" ^>nul
if not errorlevel 1 (
    echo  FreeCAD is open. Close it before rebuilding so it cannot overwrite
    echo  the newly generated library when it exits.
    pause
    exit /b 1
)

"%FREECADCMD%" "%KIT%src\build_creator_shapes.py"
if errorlevel 1 goto :failed
"%FREECADCMD%" "%KIT%src\verify_creator_shapes.py"
if errorlevel 1 goto :failed

echo.
echo  Done. The editable library is:
echo    %KIT%cad\creator-shapes.FCStd
echo.
pause
exit /b 0

:failed
echo.
echo  The rebuild failed. Keep this window open and show its message to an agent.
pause
exit /b 1
