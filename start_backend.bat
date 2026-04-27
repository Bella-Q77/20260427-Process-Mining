@echo off
echo ========================================
echo  财务单据流程挖掘系统 - 后端服务启动
echo ========================================
echo.

cd /d "%~dp0backend"

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.9+
    pause
    exit /b 1
)

echo 检查虚拟环境...
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo 检查依赖...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo 安装依赖...
    pip install -r requirements.txt
)

echo.
echo ========================================
echo  启动后端服务...
echo  服务地址: http://localhost:5000
echo ========================================
echo.

python app.py

pause
