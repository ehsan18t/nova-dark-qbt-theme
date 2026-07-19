@echo off
setlocal EnableExtensions

REM ===========================================================================
REM Nova Dark - one-click Windows build. No Docker, no Git Bash.
REM
REM This finds a Python and runs build.py, which is the actual build. It stays a
REM launcher on purpose: a .bat that reimplemented the build is what let the
REM Windows path silently package a stale stylesheet for as long as it did, so
REM there is deliberately nothing here that could drift out of sync. Add logic
REM to build.py instead.
REM
REM Needs Python 3 and qtsass (py -m pip install qtsass). Qt's rcc is NOT
REM needed - make-resource.py falls back to the bundled src\tools\rcc.exe.
REM ===========================================================================

REM %~dp0 is this file's own directory (scripts\), so ".." is the repo root.
cd /d "%~dp0.."

REM python before py, deliberately. An activated virtualenv puts its own
REM python.exe first on PATH, but the py launcher ignores virtualenvs entirely
REM and would resolve to the system install, where qtsass is probably not
REM installed. py is the fallback for a stock Windows box where python.exe is
REM absent or is the Store alias stub - which the check below rejects anyway.
set "PY="
call :find_python python.exe
if not defined PY call :find_python python3.exe
if not defined PY call :find_python py.exe

if not defined PY (
    echo [error] No working Python 3 found ^(tried python, python3, py^).
    echo         Install it from https://www.python.org/downloads/ and tick
    echo         "Add python.exe to PATH" in the installer.
    echo         Or build in Docker, which needs no local toolchain:
    echo             docker compose run --rm build
    set "RC=1"
    goto :done
)

"%PY%" "%~dp0build.py"
set "RC=%ERRORLEVEL%"

echo.
if "%RC%"=="0" (
    echo Done. Install dist\nova-dark.qbtheme via
    echo   qBittorrent - Options - Behavior - Use custom UI theme
) else (
    echo Build FAILED with exit code %RC%. See the errors above.
)

:done
REM Pause only when double-clicked from Explorer, so the window does not vanish
REM before the errors can be read. Run from a terminal, it returns immediately.
echo %cmdcmdline% | find /i "%~nx0" > nul
if not errorlevel 1 (
    echo.
    pause
)
exit /b %RC%

REM ---------------------------------------------------------------------------
REM Sets PY to the given executable if it is on PATH AND actually runs. The
REM second half matters: on Windows "python" is frequently the Microsoft Store
REM alias stub, which resolves fine and then refuses to execute.
REM ---------------------------------------------------------------------------
:find_python
set "CAND=%~$PATH:1"
if not defined CAND exit /b
"%CAND%" -c "" > nul 2>&1
if errorlevel 1 exit /b
set "PY=%CAND%"
exit /b
