# Installation requirements for CyberSecurityApp
$ErrorActionPreference = 'Stop'

Write-Host '=== CyberSecurityApp Installation Requirements ===' -ForegroundColor Cyan
Write-Host 'Steps run one-by-one. Next step starts only after previous step finishes.' -ForegroundColor DarkCyan

$kaliExists = $false
try {
    $distroList = wsl -l -q 2>$null
    foreach ($d in $distroList) {
        if ("$d".Trim().ToLower() -eq "kali-linux") {
            $kaliExists = $true
            break
        }
    }
}
catch {
    $kaliExists = $false
}

$steps = @(
    [pscustomobject]@{ Name = 'Install WSL core'; Command = 'wsl --install'; StopOnError = $false },
    [pscustomobject]@{ Name = 'Set WSL default version to 2'; Command = 'wsl --set-default-version 2'; StopOnError = $false },
    [pscustomobject]@{ Name = 'Install Kali distro'; Command = 'wsl --install -d kali-linux'; StopOnError = $false },
    [pscustomobject]@{ Name = 'Hide Kali login banner'; Command = 'wsl -d kali-linux -u root -- bash -lc "touch /root/.hushlogin; if id -u kali >/dev/null 2>&1; then touch /home/kali/.hushlogin; fi"'; StopOnError = $false },
    [pscustomobject]@{ Name = 'Update apt in Kali'; Command = 'wsl -d kali-linux -u root -- bash -lc "DEBIAN_FRONTEND=noninteractive apt update -y"'; StopOnError = $true },
    [pscustomobject]@{ Name = 'Install base tools'; Command = 'wsl -d kali-linux -u root -- bash -lc "DEBIAN_FRONTEND=noninteractive apt install -y net-tools curl macchanger tor torsocks netcat-traditional"'; StopOnError = $false },
    [pscustomobject]@{ Name = 'Install network & wireless tools'; Command = 'wsl -d kali-linux -u root -- bash -lc "DEBIAN_FRONTEND=noninteractive apt install -y nmap masscan tcpdump aircrack-ng wifite reaver"'; StopOnError = $false },
    [pscustomobject]@{ Name = 'Install password & web tools'; Command = 'wsl -d kali-linux -u root -- bash -lc "DEBIAN_FRONTEND=noninteractive apt install -y john hashcat hydra crunch sqlmap nikto gobuster whatweb wpscan medusa"'; StopOnError = $false },
    [pscustomobject]@{ Name = 'Install forensics tools'; Command = 'wsl -d kali-linux -u root -- bash -lc "DEBIAN_FRONTEND=noninteractive apt install -y binwalk foremost python3-pip; if command -v vol >/dev/null 2>&1; then echo \"[INFO] Volatility is already available.\"; elif apt-cache show volatility3 >/dev/null 2>&1; then apt install -y volatility3; else echo \"[INFO] volatility3 package is not available in apt. Trying pip install...\"; python3 -m pip install --break-system-packages -U volatility3 || true; fi; if command -v vol >/dev/null 2>&1; then echo \"[OK] Volatility command available: vol\"; else echo \"[WARN] Volatility was not installed automatically. Retry later with: python3 -m pip install --break-system-packages -U volatility3\"; fi"'; StopOnError = $false }
)

if ($kaliExists) {
    Write-Host ''
    Write-Host '[INFO] kali-linux is already installed. Step "Install Kali distro" will be skipped.' -ForegroundColor DarkCyan
}

$ok = 0
$failed = 0

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    Write-Host ''
    Write-Host ("[{0}/{1}] {2}" -f ($i + 1), $steps.Count, $step.Name) -ForegroundColor White
    Write-Host ("[RUN] {0}" -f $step.Command) -ForegroundColor Yellow

    if ($kaliExists -and ($step.Name -eq 'Install WSL core' -or $step.Name -eq 'Install Kali distro')) {
        $ok++
        Write-Host '[SKIP] Already installed.' -ForegroundColor Green
        continue
    }

    cmd.exe /c $step.Command
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        $ok++
        Write-Host ("[OK] ExitCode=0") -ForegroundColor Green
    }
    else {
        $failed++
        Write-Host ("[FAIL] ExitCode={0}" -f $exitCode) -ForegroundColor Red
        if ($step.StopOnError) {
            Write-Host 'Stopping because this step is marked as required.' -ForegroundColor Red
            break
        }
        Write-Host 'Continuing to next step because this step is non-blocking.' -ForegroundColor DarkYellow
    }
}

Write-Host ''
Write-Host ("=== Done | Success: {0}, Failed: {1} ===" -f $ok, $failed) -ForegroundColor Cyan
Write-Host 'If WSL reported restart required, reboot Windows then re-run this script.' -ForegroundColor DarkYellow
Read-Host 'Press Enter to close'
