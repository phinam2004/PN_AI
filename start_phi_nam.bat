@echo off
chcp 65001 >nul
title Phi Nam AI - Trợ Lý Ảo Máy Tính
cd /d "%~dp0"

echo ================================================================
echo   KHỞI ĐỘNG TRỢ LÝ ẢO PHI NAM AI (GIỌNG NÓI TRÊN MÁY TÍNH)
echo   Từ khóa kích hoạt: "Phi Nam" hoặc "Phi Nam ơi"
echo ================================================================
echo.

python phi_nam_assistant.py
pause
