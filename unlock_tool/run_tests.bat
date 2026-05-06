@echo off
set ROOT_DIR=%~dp0
set VENV_DIR=%ROOT_DIR%\.venv_tests
if not exist "%VENV_DIR%\Scripts\python.exe" (
    python -m venv "%VENV_DIR%"
    call "%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
    call "%VENV_DIR%\Scripts\python.exe" -m pip install requests pytest
)
call "%VENV_DIR%\Scripts\python.exe" -m pytest "%ROOT_DIR%\tests"
