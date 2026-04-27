@echo off
chcp 65001 >nul
echo ========================================
echo  财务单据流程挖掘系统 - 后端服务
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend

cd /d "%BACKEND_DIR%"

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python！
    echo 请先安装Python 3.9或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo 检查虚拟环境...
if not exist "venv" (
    echo.
    echo [警告] 未找到虚拟环境！
    echo 请先运行 install.bat 安装依赖
    echo 或手动创建虚拟环境: python -m venv venv
    echo.
    pause
    exit /b 1
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo ========================================
echo  启动后端服务...
echo  服务地址: http://localhost:5000
echo  API文档: http://localhost:5000/api/health
echo ========================================
echo.
echo 按 Ctrl+C 停止服务
echo.

python app.py

if errorlevel 1 (
    echo.
    echo [错误] 服务启动失败！
    echo 请检查是否已安装所有依赖（运行 install.bat）
    pause
)
