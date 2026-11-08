@echo off
chcp 65001 >nul
title 简易量化模拟盘 - 一键启动
color 0A

echo.
echo  ========================================
echo       简易量化模拟盘  一键启动
echo  ========================================
echo.
echo  正在检查环境，请稍等...
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [错误] 没有检测到 Python！
    echo.
    echo  请先安装 Python（推荐 3.10 或 3.11）：
    echo  1. 打开 https://www.python.org/downloads/
    echo  2. 下载并安装，安装时务必勾选 "Add Python to PATH"
    echo  3. 安装完成后重新双击本文件
    echo.
    pause
    exit /b 1
)

echo  [1/2] 正在安装必要库（第一次会慢一点）...
pip install akshare pandas -q --disable-pip-version-check
if errorlevel 1 (
    echo  [警告] 自动安装失败，尝试继续运行...
)

echo  [2/2] 正在启动模拟盘窗口...
echo.
echo  即将弹出图形界面窗口，请在窗口里点击【开始模拟交易】
echo.

python "简易量化模拟盘.py"

if errorlevel 1 (
    echo.
    echo  程序异常退出，请把上面的错误信息截图发给我。
    pause
)
