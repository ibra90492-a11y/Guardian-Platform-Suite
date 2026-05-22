\# Router Security Audit Toolkit - PowerShell Version

Clear-Host

# Define Colors
$GREEN = "`e[32m"
$RED = "`e[31m"
$CYAN = "`e[36m"
$YELLOW = "`e[33m"
$RESET = "`e[0m"

Write-Host "${CYAN}"
Write-Host "======================================================" 
Write-Host "        Router Security Audit Toolkit"
Write-Host "======================================================" 
Write-Host "${RESET}"

# Check for required tools
$TOOLS = @("nmap")

foreach ($tool in $TOOLS) {
    try {
        $null = Get-Command $tool -ErrorAction Stop
    } catch {
        Write-Host "${RED}[!] الأداة غير مثبتة: $tool${RESET}"
        Write-Host "قم بتثبيتها من: https://nmap.org/download.html"
        exit 1
    }
}

# Get Router IP
$ROUTER_IP = (Get-NetRoute | Where-Object {$_.DestinationPrefix -eq '0.0.0.0/0'} | Select-Object -First 1).NextHop
$ROUTER_IP = $ROUTER_IP -replace '\s',''

Write-Host "${GREEN}[✓] Router IP:${RESET} $ROUTER_IP"
Write-Host ""

# Network Interfaces
Write-Host "${CYAN}================ Network Interfaces =================${RESET}"
Get-NetIPAddress -AddressFamily IPv4 | Format-Table InterfaceAlias, IPAddress
Write-Host ""

# Connected Devices (ARP Table)
Write-Host "${CYAN}================ Connected Devices ==================${RESET}"
Get-NetNeighbor -AddressFamily IPv4 | Where-Object {$_.State -eq 'Reachable'} | Format-Table IPAddress, LinkLayerAddress, InterfaceAlias
Write-Host ""

# Router Port Scan
Write-Host "${CYAN}================ Router Port Scan ===================${RESET}"
Write-Host "تشغيل فحص nmap (قد يأخذ بعض الوقت)..."
nmap -sV $ROUTER_IP
Write-Host ""

# Nearby WiFi Networks
Write-Host "${CYAN}================ Nearby WiFi Networks ===============${RESET}"
try {
    netsh wlan show networks mode=Bssid | Select-String "SSID", "Signal"
} catch {
    Write-Host "تحتاج إلى تشغيل الكمبيوتر كمسؤول (Admin) لعرض شبكات WiFi"
}
Write-Host ""

# Security Recommendations
Write-Host "${CYAN}================ Security Recommendations ===========${RESET}"

Write-Host "${YELLOW}"
Write-Host "1. استخدم WPA2 أو WPA3 فقط"
Write-Host "2. عطّل WPS من إعدادات المودم"
Write-Host "3. غيّر كلمة مرور admin الافتراضية"
Write-Host "4. حدّث Firmware المودم"
Write-Host "5. راقب الأجهزة المتصلة باستمرار"
Write-Host "6. استخدم كلمة مرور WiFi قوية"
Write-Host "${RESET}"

Write-Host "${GREEN}✓ انتهى الفحص الأمني للشبكة.${RESET}"
