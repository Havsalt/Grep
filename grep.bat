@echo off

@REM == Batch script for running python command line script ==
@REM Activates the project's .venv
@REM Runs script as python module
@REM Exits with script's exit code

call %~dp0\.venv\Scripts\activate.bat
python -m grep %*


@REM The following part is from `deactivate.bat`
@REM It is usually found in .venv\Scripts\deactivate.bat

@set VIRTUAL_ENV=
@set VIRTUAL_ENV_PROMPT=

@REM Don't use () to avoid problems with them in %PATH%
@if not defined _OLD_VIRTUAL_PROMPT @goto ENDIFVPROMPT
    @set "PROMPT=%_OLD_VIRTUAL_PROMPT%"
    @set _OLD_VIRTUAL_PROMPT=
:ENDIFVPROMPT

@if not defined _OLD_VIRTUAL_PYTHONHOME @goto ENDIFVHOME
    @set "PYTHONHOME=%_OLD_VIRTUAL_PYTHONHOME%"
    @set _OLD_VIRTUAL_PYTHONHOME=
:ENDIFVHOME

@if not defined _OLD_VIRTUAL_PATH @goto ENDIFVPATH
    @set "PATH=%_OLD_VIRTUAL_PATH%"
    @set _OLD_VIRTUAL_PATH=
:ENDIFVPATH

@REM Bubble up exit code from script, to parent process
exit /b %ERRORLEVEL%
