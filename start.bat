@echo off
echo ========================================
echo   CursorUnlimited 启动脚本
echo ========================================
echo.

echo [1/3] 清理Python缓存文件...
echo --------------------------------------

:: 删除所有 __pycache__ 目录
for /d /r %%d in (__pycache__) do @if exist "%%d" (
    echo 删除: %%d
    rd /s /q "%%d"
)

:: 删除所有 .pyc 文件
for /r %%f in (*.pyc) do @if exist "%%f" (
    echo 删除: %%f
    del /q "%%f"
)

:: 删除所有 .pyo 文件
for /r %%f in (*.pyo) do @if exist "%%f" (
    echo 删除: %%f
    del /q "%%f"
)

:: 删除所有 .pyd 文件（可选，这些是编译的扩展模块）
:: for /r %%f in (*.pyd) do @if exist "%%f" del /q "%%f"

echo.
echo [2/3] 缓存清理完成！
echo --------------------------------------
echo.

:: 检查Python是否安装
echo [3/3] 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo Python环境正常
echo.

:: 启动主程序
echo 正在启动 CursorUnlimited...
echo ========================================
python main.py

:: 如果程序异常退出，暂停以查看错误信息
if %errorlevel% neq 0 (
    echo.
    echo 程序异常退出，错误代码: %errorlevel%
    pause
)