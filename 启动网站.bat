@echo off
rem start local preview of the Columbia site
cd /d "%~dp0"
start "" http://127.0.0.1:8811/
python -m http.server 8811 --bind 127.0.0.1
