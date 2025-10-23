@echo off
setlocal enabledelayedexpansion

set ROOT_DIR=%~dp0
set ROOT_DIR=%ROOT_DIR:~0,-1%
set THEME_ROOT=%ROOT_DIR%\nova-dark
set SRC_DIR=%THEME_ROOT%\source
set ICONS_DIR=%THEME_ROOT%\icons\modern
set CONFIG_FILE=%THEME_ROOT%\nova-dark-config.json
set DIST_DIR=%ROOT_DIR%\dist
set OUTPUT_PREFIX=nova-dark
set COMMON_DIR=%ROOT_DIR%\common

if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

for /f %%G in ('dir /b "%ICONS_DIR%\*.svg" 2^>nul') do set FOUND_ICON=1
if not defined FOUND_ICON (
  1>&2 echo [warn] No SVG icons detected in src\nova-dark\icons\modern
  1>&2 echo [warn] Copy the Mumble Dark icon set here ^(or provide your own^) before packaging.
)

pushd "%SRC_DIR%"
qtsass -o ..\NovaDark.qss NovaDark.scss
popd

python "%ROOT_DIR%\make-resource.py" ^
  -base-dir "%THEME_ROOT%" ^
  -find-files ^
  -config "%CONFIG_FILE%" ^
  -icons-dir "%ICONS_DIR%" ^
  -include-dir "%COMMON_DIR%" ^
  -output "%DIST_DIR%\%OUTPUT_PREFIX%-modern" ^
  -style NovaDark.qss

python "%ROOT_DIR%\make-resource.py" ^
  -base-dir "%THEME_ROOT%" ^
  -find-files ^
  -config "%CONFIG_FILE%" ^
  -include-dir "%COMMON_DIR%" ^
  -output "%DIST_DIR%\%OUTPUT_PREFIX%-no-icons" ^
  -style NovaDark.qss
