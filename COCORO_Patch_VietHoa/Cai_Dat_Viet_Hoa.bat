@echo off
chcp 65001 >nul
title COCORO - Cài Đặt Patch Việt Hóa
if exist "%~dp0Cai_Dat_Viet_Hoa.exe" (
    start "" "%~dp0Cai_Dat_Viet_Hoa.exe"
) else (
    py -3 "%~dp0patcher_gui.py"
)
exit
