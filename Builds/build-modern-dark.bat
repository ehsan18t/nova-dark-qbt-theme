@echo off
setlocal enabledelayedexpansion

set ROOT_DIR=%~dp0
set ROOT_DIR=%ROOT_DIR:~0,-1%
set THEME_ROOT=%ROOT_DIR%\modern-dark
set SRC_DIR=%THEME_ROOT%\source
set ICONS_DIR=%THEME_ROOT%\icons\modern
set TEMP_ICONS_DIR=%THEME_ROOT%\.icons-recolored
set TEMP_COMMON_DIR=%ROOT_DIR%\.common-recolored
set CONFIG_FILE=%THEME_ROOT%\modern-dark-config.json
set DIST_DIR=%ROOT_DIR%\dist
set OUTPUT_PREFIX=nova-dark
set COMMON_DIR=%ROOT_DIR%\common
set DEFINITIONS_FILE=%SRC_DIR%\Imports\Nova Definitions.scss

if not exist "%DIST_DIR%" mkdir "%DIST_DIR%"

for /f %%G in ('dir /b "%ICONS_DIR%\*.svg" 2^>nul') do set FOUND_ICON=1
if not defined FOUND_ICON (
  1>&2 echo [warn] No SVG icons detected in Builds\modern-dark\icons\modern
  1>&2 echo [warn] Copy the Mumble Dark icon set here ^(or provide your own^) before packaging.
)

pushd "%SRC_DIR%"
qtsass -o ..\ModernDark.qss ModernDark.scss
popd

echo [info] Recoloring icons based on theme accent color...
python "%ROOT_DIR%\recolor-icons.py" "%DEFINITIONS_FILE%" "%ICONS_DIR%" "%TEMP_ICONS_DIR%"
python "%ROOT_DIR%\recolor-icons.py" "%DEFINITIONS_FILE%" "%COMMON_DIR%\controls" "%TEMP_COMMON_DIR%\controls"

echo [info] Recoloring icons based on theme accent color...
python "%ROOT_DIR%\recolor-icons.py" "%DEFINITIONS_FILE%" "%ICONS_DIR%" "%TEMP_ICONS_DIR%"
python "%ROOT_DIR%\recolor-icons.py" "%DEFINITIONS_FILE%" "%COMMON_DIR%\controls" "%TEMP_COMMON_DIR%\controls"

python "%ROOT_DIR%\make-resource.py" ^
  -base-dir "%THEME_ROOT%" ^
  -find-files ^
  -config "%CONFIG_FILE%" ^
  -icons-dir "%TEMP_ICONS_DIR%" ^
  -include-dir "%TEMP_COMMON_DIR%" ^
  -output "%DIST_DIR%\%OUTPUT_PREFIX%-modern" ^
  -style ModernDark.qss

python "%ROOT_DIR%\make-resource.py" ^
  -base-dir "%THEME_ROOT%" ^
  -find-files ^
  -config "%CONFIG_FILE%" ^
  -include-dir "%TEMP_COMMON_DIR%" ^
  -output "%DIST_DIR%\%OUTPUT_PREFIX%-no-icons" ^
  -style ModernDark.qss

if exist "%TEMP_ICONS_DIR%" rd /s /q "%TEMP_ICONS_DIR%"
if exist "%TEMP_COMMON_DIR%" rd /s /q "%TEMP_COMMON_DIR%"
