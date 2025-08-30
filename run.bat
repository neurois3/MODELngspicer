@echo off
setlocal

REM Check Python version
python -c "import sys; exit(0) if sys.version_info >= (3,13) else exit(1)"
if errorlevel 1 (
    echo [ERROR] Python 3.13 or later is required.
    goto end
)

REM Check required Python packages
python -c "import PySide6, pyqtgraph, numpy" 2>nul
if errorlevel 1 (
    echo [ERROR] Required Python packages are missing: PySide6, pyqtgraph, numpy
    goto end
)

REM Check ngspice_con command
where ngspice_con >nul 2>nul
if errorlevel 1 (
    echo [ERROR] ngspice_con command not found in PATH.
    goto end
)

REM Launch application
python src/main.py
goto end

:end
endlocal
