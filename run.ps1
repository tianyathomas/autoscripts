# 爱奇艺签到启动脚本 (Windows PowerShell)
# 使用方法: .\run.ps1

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 检查 .env 文件是否存在
$envFile = Join-Path $scriptDir ".env"
if (Test-Path $envFile) {
    Write-Host "正在加载 .env 文件..."
    Get-Content $envFile | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            $name = $matches[1].Trim()
            $value = $matches[2].Trim()
            # 移除可能的引号
            $value = $value -replace '^["'']|["'']$', ''
            [Environment]::SetEnvironmentVariable($name, $value, "Process")
        }
    }
}

# 检查环境变量
if (-not $env:IQIYI_COOKIE) {
    Write-Host "错误: 未设置 IQIYI_COOKIE 环境变量" -ForegroundColor Red
    Write-Host ""
    Write-Host "请选择以下方式之一设置 Cookie:"
    Write-Host ""
    Write-Host "方式一: 创建 .env 文件"
    Write-Host "  1. 复制 .env.example 为 .env"
    Write-Host "  2. 编辑 .env 文件，填入你的 Cookie"
    Write-Host ""
    Write-Host "方式二: 直接设置环境变量"
    Write-Host "  `$env:IQIYI_COOKIE=`"P00001=xxx; P00002=xxx; ...`""
    Write-Host ""
    exit 1
}

# 运行签到脚本
$scriptPath = Join-Path $scriptDir "iqiyi.js"
Write-Host "启动爱奇艺签到..."
Write-Host ""
node $scriptPath
