@echo off
chcp 65001 >nul
title 抖音直播AI回复助手
cd /d "%~dp0scripts"
echo ============================================================
echo  抖音直播AI回复助手 - 启动中...
echo ============================================================
python main_with_reconnect.py
pause
