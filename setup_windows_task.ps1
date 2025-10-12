# 博牛社区爬虫Windows任务计划程序设置脚本
# 每两天晚上11点执行一次

param(
    [string]$TaskName = "博牛社区爬虫定时任务",
    [string]$Description = "每两天晚上11点执行博牛社区爬虫任务"
)

# 获取脚本所在目录
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "设置博牛社区爬虫Windows定时任务..." -ForegroundColor Green
Write-Host "项目目录: $ScriptDir" -ForegroundColor Yellow

# 检查是否以管理员权限运行
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "错误: 需要管理员权限来创建任务计划程序任务" -ForegroundColor Red
    Write-Host "请以管理员身份运行PowerShell" -ForegroundColor Red
    exit 1
}

# 检查任务是否已存在
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
if ($ExistingTask) {
    Write-Host "警告: 任务 '$TaskName' 已存在" -ForegroundColor Yellow
    $response = Read-Host "是否要删除现有任务并重新创建? (y/N)"
    if ($response -eq 'y' -or $response -eq 'Y') {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
        Write-Host "已删除现有任务" -ForegroundColor Green
    } else {
        Write-Host "取消设置" -ForegroundColor Yellow
        exit 0
    }
}

# 创建任务动作
$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$ScriptDir\run_scheduled_crawler.bat`""

# 创建任务触发器（每两天晚上11点）
$Trigger = New-ScheduledTaskTrigger -Daily -At "23:00" -DaysInterval 2

# 创建任务设置
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# 创建任务主体（使用SYSTEM账户）
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# 注册任务
try {
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description $Description
    
    Write-Host "定时任务设置成功!" -ForegroundColor Green
    Write-Host ""
    Write-Host "任务详情:" -ForegroundColor Cyan
    Write-Host "- 任务名称: $TaskName" -ForegroundColor White
    Write-Host "- 执行时间: 每两天晚上11点" -ForegroundColor White
    Write-Host "- 执行脚本: $ScriptDir\run_scheduled_crawler.bat" -ForegroundColor White
    Write-Host "- 日志目录: $ScriptDir\logs\scheduled\" -ForegroundColor White
    Write-Host ""
    Write-Host "管理命令:" -ForegroundColor Cyan
    Write-Host "- 查看任务: Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host "- 运行任务: Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host "- 删除任务: Unregister-ScheduledTask -TaskName '$TaskName'" -ForegroundColor White
    Write-Host "- 任务计划程序: taskschd.msc" -ForegroundColor White
    Write-Host ""
    Write-Host "测试执行: $ScriptDir\run_scheduled_crawler.bat" -ForegroundColor Yellow
    
} catch {
    Write-Host "设置任务失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
