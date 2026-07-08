param(
    [ValidateSet("sync","restart","stop","status","full")]
    [string]$Command = "sync",
    [string]$Server = "192.168.56.101",
    [string]$User = "root",
    [string]$Password = "bwpass"
)

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ResPath = Join-Path $ProjectRoot "res"
$RemoteResPath = "/opt/bigworld/my_game/res"
$RemoteScripts = "/opt/bigworld/start_mygame.sh"
$PlinkArgs = "-batch -hostkey `"ssh-ed25519 255 SHA256:2ssLbmdg4euiEUol5w5E6oLFEj7ZUR4qnX489YutuRM`" -pw $Password"

function Run-Remote {
    param([string]$Cmd)
    $fullCmd = "plink $PlinkArgs $User@$Server `"$Cmd`""
    return Invoke-Expression $fullCmd
}

function Copy-ToServer {
    param([string]$LocalPath, [string]$RemotePath)
    echo "pscp $PlinkArgs -r `"$LocalPath`" $User@$Server`:$RemotePath"
    $fullCmd = "pscp $PlinkArgs -r `"$LocalPath`" $User@$Server`:$RemotePath"
    Invoke-Expression $fullCmd
}

switch ($Command) {
    "status" {
        Write-Host "=== Server Status ===" -ForegroundColor Cyan
        Run-Remote "ps aux | grep -E 'bwmachined|dbmgr|baseapp|cellapp|loginapp' | grep -v grep | grep -v bash"
        Write-Host ""
        Write-Host "=== Network ===" -ForegroundColor Cyan
        Run-Remote "ss -ulnp | grep -E '20013|20015'"
    }
    "stop" {
        Write-Host "=== Stopping Server ===" -ForegroundColor Yellow
        Run-Remote "pkill -f '/opt/bigworld/2.1/server/bigworld/bin/Hybrid64/' 2>/dev/null; pkill bwmachined2 2>/dev/null; echo 'Server stopped'"
    }
    "restart" {
        Write-Host "=== Restarting my_game Server ===" -ForegroundColor Yellow
        Run-Remote "cd /opt/bigworld && bash /opt/bigworld/start_mygame.sh > /tmp/deploy_restart.log 2>&1 &"
        Start-Sleep -Seconds 20
        Write-Host "=== Post-restart Status ===" -ForegroundColor Cyan
        Run-Remote "ps aux | grep -E 'bwmachined|dbmgr|baseapp|cellapp|loginapp' | grep -v grep | grep -v bash"
    }
    "sync" {
        Write-Host "=== Deploying my_game to $Server ===" -ForegroundColor Green
        if (-not (Test-Path $ResPath)) {
            Write-Host "ERROR: $ResPath not found" -ForegroundColor Red
            exit 1
        }
        Write-Host "Syncing scripts..." -ForegroundColor Cyan
        Copy-ToServer "$ResPath/scripts" "$RemoteResPath/"
        Write-Host "Syncing server config..." -ForegroundColor Cyan
        Copy-ToServer "$ResPath/server" "$RemoteResPath/"
        Write-Host "Syncing engine_config.xml..." -ForegroundColor Cyan
        Copy-ToServer "$ResPath/engine_config.xml" "$RemoteResPath/"
        Write-Host "Syncing scripts_config.xml..." -ForegroundColor Cyan
        Copy-ToServer "$ResPath/scripts_config.xml" "$RemoteResPath/"
        Write-Host "Syncing spaces..." -ForegroundColor Cyan
        Copy-ToServer "$ResPath/spaces" "$RemoteResPath/"
        Write-Host "Syncing characters..." -ForegroundColor Cyan
        Copy-ToServer "$ResPath/characters" "$RemoteResPath/"
        Write-Host "Sync complete!" -ForegroundColor Green
        Write-Host "Run 'deploy.ps1 restart' to restart server" -ForegroundColor Yellow
    }
    "full" {
        & $MyInvocation.MyCommand.Path -Command sync -Server $Server -User $User -Password $Password
        Write-Host ""
        & $MyInvocation.MyCommand.Path -Command restart -Server $Server -User $User -Password $Password
    }
}
