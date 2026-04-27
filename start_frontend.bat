@echo off
echo ========================================
echo  财务单据流程挖掘系统 - 前端服务启动
echo ========================================
echo.

cd /d "%~dp0frontend"

echo 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Node.js，请先安装Node.js 18+
    pause
    exit /b 1
)

echo 检查npm...
npm --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到npm
    pause
    exit /b 1
)

echo 检查node_modules...
if not exist "node_modules" (
    echo 安装依赖...
    npm install
)

echo.
echo ========================================
echo  启动前端服务...
echo  服务地址: http://localhost:3000
echo ========================================
echo.

npm run dev

pause
