@echo off
setlocal enabledelayedexpansion

set SCRIPTS_DIR=%~dp0
set SCRIPTS_DIR=%SCRIPTS_DIR:~0,-1%
call "%SCRIPTS_DIR%\build-support.bat"

set THEME_ROOT=%SRC_ROOT%\nova-dark
set SRC_DIR=%THEME_ROOT%\source
set ICONS_DIR=%THEME_ROOT%\icons\modern
set CONFIG_FILE=%THEME_ROOT%\nova-dark-config.json
set OUTPUT_PREFIX=nova-dark
set COMMON_DIR=%SRC_ROOT%\common

set FOUND_ICON=

for /f %%G in ('dir /b "%ICONS_DIR%\*.svg" 2^>nul') do set FOUND_ICON=1
if not defined FOUND_ICON (
  1>&2 echo [warn] No SVG icons detected in src\nova-dark\icons\modern
  1>&2 echo [warn] Copy the Mumble Dark icon set here ^(or provide your own^) before packaging.
)

pushd "%SRC_DIR%"
qtsass -o ..\NovaDark.qss NovaDark.scss
popd

python "%SRC_ROOT%\make-resource.py" ^
  -base-dir "%THEME_ROOT%" ^
  -find-files ^
  -config "%CONFIG_FILE%" ^
  -icons-dir "%ICONS_DIR%" ^
  -include-dir "%COMMON_DIR%" ^
  -output "%DIST_DIR%\%OUTPUT_PREFIX%-modern" ^
  -style NovaDark.qss

python "%SRC_ROOT%\make-resource.py" ^
  -base-dir "%THEME_ROOT%" ^
  -find-files ^
  -config "%CONFIG_FILE%" ^
  -include-dir "%COMMON_DIR%" ^
  -output "%DIST_DIR%\%OUTPUT_PREFIX%-no-icons" ^
  -style NovaDark.qss

endlocal
