@echo off
set SRC_ROOT=%~dp0
set SRC_ROOT=%SRC_ROOT:~0,-1%
for %%I in ("%SRC_ROOT%\..") do set PROJECT_ROOT=%%~fI
set DIST_DIR=%PROJECT_ROOT%\dist
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"
goto :EOF
