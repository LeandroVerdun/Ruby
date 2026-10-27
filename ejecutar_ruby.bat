
@echo off
cd /d "%~dp0"
call "%~dp0ruby-voz-test\Scripts\activate.bat"
python main.py
pause
