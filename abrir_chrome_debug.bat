@echo off
cd /d "%~dp0"
start chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\ChromeDebug"
