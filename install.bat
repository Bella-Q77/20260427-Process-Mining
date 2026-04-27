@echo off
chcp 65001 >nul
echo ========================================
echo  财务单据流程挖掘系统 - 安装依赖
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend
set FRONTEND_DIR=%SCRIPT_DIR%frontend

echo [1/2] 检查并安装后端依赖...
cd /d "%BACKEND_DIR%"

echo.
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

echo Python版本检查通过。
echo.

if not exist "venv" (
    echo 创建Python虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat

echo.
echo 安装后端Python依赖...
pip install -r requirements.txt
if errorlevel 1 (
    echo [错误] 安装后端依赖失败
    pause
    exit /b 1
)
echo 后端依赖安装完成！

echo.
echo [2/2] 检查并安装前端依赖...
cd /d "%FRONTEND_DIR%"

echo.
echo 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [警告] 未找到Node.js，前端依赖将不会安装
    echo 如需使用前端，请安装Node.js 18或更高版本
    echo 下载地址: https://nodejs.org/
    echo.
) else (
    echo Node.js版本检查通过。
    
    if not exist "node_modules" (
        echo.
        echo 安装前端npm依赖...
        npm install
        if errorlevel 1 (
            echo [警告] 安装前端依赖失败，您可以稍后手动运行 npm install
        ) else (
            echo 前端依赖安装完成！
        )
    ) else (
        echo 前端依赖已存在，跳过安装。
    )
)

echo.
echo ========================================
echo  依赖安装完成！
echo ========================================
echo.
echo 接下来请按以下步骤启动系统：
echo.
echo 1. 启动后端服务:
echo    双击运行 start_backend.bat
echo    或手动执行: cd backend ^&^& venv\Scripts\activate ^&^& python app.py
echo.
echo 2. 启动前端服务（需要Node.js）:
echo    双击运行 start_frontend.bat
echo    或手动执行: cd frontend ^&^& npm run dev
echo.
echo 3. 访问系统:
echo    前端地址: http://localhost:3000
echo    后端API: http://localhost:5000
echo.
pause
