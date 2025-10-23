@echo off
setlocal enabledelayedexpansion

set SCRIPTS_DIR=%~dp0
set SCRIPTS_DIR=%SCRIPTS_DIR:~0,-1%
call "%SCRIPTS_DIR%\build-support.bat"

set ROOT_DIR=%SRC_ROOT%
set THEME_DIR=%ROOT_DIR%\mumble-theme
set SRC_DIR=%THEME_DIR%\source
set CONFIG_FILE=%ROOT_DIR%\dark-config.json
set OUTPUT_BASE=mumble-dark

pushd "%SRC_DIR%"
qtsass -o ..\Dark.qss Dark.scss
popd

set ICON_WORKDIR=%THEME_DIR%\mumble-icons
if exist "%ICON_WORKDIR%" rd /s /q "%ICON_WORKDIR%"
mkdir "%ICON_WORKDIR%"

python "%SRC_ROOT%\fill-icons.py" nowshed #4B9CD3 "%ICON_WORKDIR%"

python "%SRC_ROOT%\make-resource.py" ^
  -base-dir "%THEME_DIR%" ^
  -find-files ^
  -config "%CONFIG_FILE%" ^
  -icons-dir "%ICON_WORKDIR%" ^
  -output "%DIST_DIR%\%OUTPUT_BASE%-nowshed-recolored" ^
  -style Dark.qss

if exist "%ICON_WORKDIR%" rd /s /q "%ICON_WORKDIR%"

python "%SRC_ROOT%\make-resource.py" ^
  -base-dir "%THEME_DIR%" ^
  -find-files ^
  -config "%CONFIG_FILE%" ^
  -icons-dir "%THEME_DIR%\icons\nowshed" ^
  -output "%DIST_DIR%\%OUTPUT_BASE%-nowshed" ^
  -style Dark.qss

endlocal
