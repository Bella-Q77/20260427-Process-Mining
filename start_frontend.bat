@echo off
chcp 65001 >nul
echo ========================================
echo  财务单据流程挖掘系统 - 前端服务
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
set FRONTEND_DIR=%SCRIPT_DIR%frontend

cd /d "%FRONTEND_DIR%"

echo 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Node.js！
    echo 请先安装Node.js 18或更高版本
    echo 下载地址: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo 检查npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到npm
    echo 请确保Node.js安装完整
    pause
    exit /b 1
)

echo 检查node_modules...
if not exist "node_modules" (
    echo.
    echo [警告] 未找到依赖包！
    echo 正在自动安装依赖...
    echo.
    npm install
    if errorlevel 1 (
        echo.
        echo [错误] 安装依赖失败
        echo 请手动执行: npm install
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo  启动前端服务...
echo  服务地址: http://localhost:3000
echo ========================================
echo.
echo 按 Ctrl+C 停止服务
echo.

npm run dev

if errorlevel 1 (
    echo.
    echo [错误] 服务启动失败！
    echo 请检查是否已安装所有依赖（运行 npm install）
    pause
)
