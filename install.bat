@echo off
chcp 65001 >nul
echo ========================================
echo  财务单据流程挖掘系统 - 安装依赖
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
set BACKEND_DIR=%SCRIPT_DIR%backend
set FRONTEND_DIR=%SCRIPT_DIR%frontend

echo [1/2] 安装后端依赖...
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

echo 安装后端依赖...
pip install Flask Flask-CORS Flask-SQLAlchemy pandas numpy matplotlib networkx python-dateutil pytz pm4py
if errorlevel 1 (
    echo [警告] 部分依赖安装可能遇到问题
    echo 但基础功能应该可以使用
)
echo 后端依赖安装完成！

echo.
echo [2/2] 安装前端依赖...
cd /d "%FRONTEND_DIR%"

echo.
echo 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo [警告] 未找到Node.js，前端依赖将不会安装
    echo 如需使用前端，请安装Node.js 18或更高版本
    echo 下载地址: https://nodejs.org/
    echo.
    goto skip_frontend
)

echo Node.js版本检查通过。
echo.

if not exist "node_modules" (
    echo 安装前端npm依赖...
    npm install
    if errorlevel 1 (
        echo [警告] 前端依赖安装失败
        echo 请稍后手动运行: npm install
    ) else (
        echo 前端依赖安装完成！
    )
) else (
    echo 前端依赖已存在，跳过安装。
)

:skip_frontend

echo.
echo ========================================
echo  依赖安装完成！
echo ========================================
echo.
echo 启动方式：
echo.
echo 方式一（推荐）：分别打开两个命令窗口
echo   窗口1：双击 start_backend.bat
echo   窗口2：双击 start_frontend.bat
echo.
echo 方式二：手动命令行启动
echo   启动后端: cd backend ^&^& python app.py
echo   启动前端: cd frontend ^&^& npm run dev
echo.
echo 访问地址：
echo   前端界面: http://localhost:3000
echo   后端API: http://localhost:5000
echo.
pause
