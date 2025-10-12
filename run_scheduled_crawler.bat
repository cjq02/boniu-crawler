@echo off
REM 博牛社区爬虫定时任务批处理文件
REM 每两天晚上11点执行一次

REM 设置编码为UTF-8
chcp 65001 >nul

REM 获取脚本所在目录
set SCRIPT_DIR=%~dp0

REM 切换到项目根目录
cd /d "%SCRIPT_DIR%"

REM 激活虚拟环境（如果存在）
if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
)

REM 执行Python爬虫脚本
echo 开始执行博牛社区爬虫定时任务...
echo 执行时间: %date% %time%
echo 项目目录: %SCRIPT_DIR%

python src\scheduler\scheduled_crawler.py

REM 检查执行结果
if %errorlevel% equ 0 (
    echo 爬虫任务执行成功
) else (
    echo 爬虫任务执行失败，错误代码: %errorlevel%
)

exit /b %errorlevel%
