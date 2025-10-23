@echo off
set SCRIPTS_DIR=%~dp0
set SCRIPTS_DIR=%SCRIPTS_DIR:~0,-1%
for %%I in ("%SCRIPTS_DIR%\..") do set PROJECT_ROOT=%%~fI
set SRC_ROOT=%PROJECT_ROOT%\src
set DIST_DIR=%PROJECT_ROOT%\dist
if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"
