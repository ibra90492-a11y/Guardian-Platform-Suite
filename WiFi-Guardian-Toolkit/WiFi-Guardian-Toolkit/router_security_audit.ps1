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
    }
    catch {
        Write-Host "${RED}[!] الأداة غير مثبتة: $tool${RESET}"
        Write-Host "قم بتثبيتها من: https://nmap.org/download.html"
        exit 1
    }
}

# Get Router IP
$ROUTER_IP = (Get-NetRoute | Where-Object { $_.DestinationPrefix -eq '0.0.0.0/0' } | Select-Object -First 1).NextHop
$ROUTER_IP = $ROUTER_IP -replace '\s', ''

Write-Host "${GREEN}[✓] Router IP:${RESET} $ROUTER_IP"
Write-Host ""

# Network Interfaces
Write-Host "${CYAN}================ Network Interfaces =================${RESET}"
Get-NetIPAddress -AddressFamily IPv4 | Format-Table InterfaceAlias, IPAddress
Write-Host ""

# Connected Devices Analysis
Write-Host "${CYAN}================ Connected Devices ==================${RESET}"

# Get all connected devices from ARP table
$connectedDevices = Get-NetNeighbor -AddressFamily IPv4 | Where-Object { $_.State -eq 'Reachable' -and $_.IPAddress -notlike '169.254.*' } | Sort-Object IPAddress

# Filter out this computer's interfaces
$macArray = (Get-NetAdapter | Select-Object -ExpandProperty MacAddress).ToLower()

# Device database for OS & Model detection
$deviceDatabase = @{
    # Apple Devices
    "00:1A:2B" = @("Apple", "MacBook/iPhone");
    "00:0A:95" = @("Apple", "MacBook");
    "00:03:93" = @("Apple", "iMac");
    "00:1D:4F" = @("Apple", "MacBook");
    "00:25:86" = @("Apple", "MacBook");
    "A4:5E:60" = @("Apple", "iPhone/iPad");
    
    # Windows/PC
    "00:11:85" = @("Windows", "3Com Network Adapter");
    "00:0C:29" = @("Windows", "VMware Virtual");
    "08:00:27" = @("Linux", "VirtualBox");
    "52:54:00" = @("Linux", "KVM/QEMU");
    
    # Routers & Networking
    "00:1C:14" = @("Router", "Cisco");
    "A4:12:69" = @("Router", "TP-Link");
    "78:AC:44" = @("Router", "TP-Link");
    "AC:84:C6" = @("Router", "Huawei");
    
    # Raspberry Pi & SBCs
    "DC:A6:32" = @("Linux", "Raspberry Pi");
    "B8:27:EB" = @("Linux", "Raspberry Pi");
    "E4:5F:01" = @("Linux", "Raspberry Pi");
    "2E:A6:D7" = @("Linux", "Raspberry Pi");
    
    # Samsung
    "2C:F0:5D" = @("Android", "Samsung Phone");
    "88:32:9B" = @("Android", "Samsung Device");
    
    # Other Devices
    "00:1F:32" = @("Windows", "HP Printer");
    "00:14:85" = @("IoT", "Belkin Smart");
    "50:C7:BF" = @("Android", "Google Device");
    "C4:AD:34" = @("iOS", "iPhone");
}

# Count devices
$deviceCount = $connectedDevices.Count
if ($null -eq $deviceCount) { $deviceCount = 1 }

Write-Host "${GREEN}[✓] عدد الأجهزة المتصلة: $deviceCount${RESET}"
Write-Host ""

# Display devices with details
$deviceList = @()
$counter = 1

foreach ($device in $connectedDevices) {
    $ip = $device.IPAddress
    $mac = $device.LinkLayerAddress.ToLower()
    $iface = $device.InterfaceAlias
    
    # Detect device type/OS from MAC address prefix
    $detectedOS = "غير معروف"
    foreach ($prefix in $deviceDatabase.Keys) {
        if ($mac.StartsWith($prefix.ToLower())) {
            $detectedOS = $deviceDatabase[$prefix]
            break
        }
    }
    
    # Try to detect model via nmap
    $model = "---"
    
    $deviceObj = [PSCustomObject]@{
        'الرقم'        = $counter
        'IP Address'   = $ip
        'MAC Address'  = $mac
        'نظام التشغيل' = $detectedOS
        'الموديل'      = $model
        'الواجهة'      = $iface
    }
    
    $deviceList += $deviceObj
    $counter++
}

# Display table
$deviceList | Format-Table -AutoSize
Write-Host ""

# Advanced scan with nmap for OS detection
Write-Host "${YELLOW}[*] جاري المسح المتقدم لاكتشاف نظام التشغيل والموديلات...${RESET}"
Write-Host ""

foreach ($device in $connectedDevices) {
    $ip = $device.IPAddress
    $mac = $device.LinkLayerAddress.ToLower()
    
    # Skip self device
    if ($macArray -contains $mac) { continue }
    
    Write-Host "${CYAN}الجهاز: $ip ($mac)${RESET}"
    
    # Try nmap to detect OS
    try {
        $nmapResult = nmap -O -n -sV "$ip" 2>$null | Select-String -Pattern "OS details|Service Info" | Select-Object -First 2
        if ($nmapResult) {
            Write-Host $nmapResult -ForegroundColor Gray
        }
    }
    catch {
        Write-Host "لم يتمكن من اكتشاف نظام التشغيل"
    }
    
    Write-Host ""
}


# Router Port Scan
Write-Host "${CYAN}================ Router Port Scan ===================${RESET}"
Write-Host "تشغيل فحص nmap (قد يأخذ بعض الوقت)..."
nmap -sV $ROUTER_IP
Write-Host ""

# WiFi Network Information
Write-Host "${CYAN}================ معلومات شبكة WiFi الحالية ===========${RESET}"

try {
    # Get current connected WiFi network
    $wifiProfiles = netsh wlan show profiles | Select-String ":" | Select-String -NotMatch "غير متصل"
    
    if ($wifiProfiles) {
        # Get current connected network
        $currentNetwork = netsh wlan show interfaces | Select-String "SSID"
        
        if ($currentNetwork) {
            $ssid = ($currentNetwork -split ":")[-1].Trim()
            
            if ($ssid -and $ssid -ne "") {
                Write-Host "${GREEN}[✓] اسم الشبكة (SSID): $ssid${RESET}"
                
                # Try to get WiFi password
                Write-Host "${YELLOW}[*] جاري البحث عن كلمة المرور...${RESET}"
                
                $wifiPasswords = @()
                $passwordFound = $false
                
                # Method 1: Get from netsh
                try {
                    $profileOutput = netsh wlan show profile name="$ssid" key=clear 2>$null
                    $passwordLine = $profileOutput | Select-String "Key Content"
                    
                    if ($passwordLine) {
                        $password = ($passwordLine -split ":")[-1].Trim()
                        if ($password -and $password -ne "") {
                            Write-Host "${GREEN}[✓] كلمة المرور: $password${RESET}"
                            $passwordFound = $true
                        }
                    }
                }
                catch {
                    Write-Host "${RED}[!] لم يتمكن من استخراج كلمة المرور (قد تحتاج صلاحيات مسؤول)${RESET}"
                }
                
                if (-not $passwordFound) {
                    Write-Host "${YELLOW}[*] تلميح: يمكنك عرض كلمة المرور بالأمر التالي كمسؤول:${RESET}"
                    Write-Host "netsh wlan show profile name=""$ssid"" key=clear"
                }
                
                # Get WiFi Security Info
                Write-Host ""
                Write-Host "${CYAN}معلومات الأمان:${RESET}"
                
                $securityInfo = netsh wlan show profile name="$ssid" | Select-String "Authentication|Encryption|Security Type"
                if ($securityInfo) {
                    $securityInfo | ForEach-Object {
                        Write-Host "  $_"
                    }
                }
            }
            else {
                Write-Host "${RED}[!] لا يوجد اتصال WiFi نشط حالياً${RESET}"
            }
        }
    }
}
catch {
    Write-Host "${RED}[!] خطأ في الوصول لمعلومات WiFi (تحتاج صلاحيات مسؤول)${RESET}"
}

Write-Host ""

# Nearby WiFi Networks with Advanced Information
Write-Host "${CYAN}================ الشبكات اللاسلكية القريبة ============${RESET}"
try {
    $wifiNetworks = netsh wlan show networks mode=Bssid
    
    # Parse and display networks with advanced details
    $networks = @()
    $currentNetwork = @{}
    $networkCount = 0
    
    foreach ($line in $wifiNetworks) {
        if ($line -match "^\s*SSID\s+\d+") {
            if ($currentNetwork.SSID) {
                $networks += $currentNetwork
            }
            $networkCount++
            $ssidValue = ($line -split ":")[-1].Trim()
            $currentNetwork = @{
                SSID  = $ssidValue
                Index = $networkCount
            }
        }
        elseif ($line -match "Signal\s*:" -and $currentNetwork.SSID) {
            $signalValue = ($line -split ":")[-1].Trim()
            $currentNetwork.Signal = $signalValue
        }
        elseif ($line -match "Channel\s*:" -and $currentNetwork.SSID) {
            $channelValue = ($line -split ":")[-1].Trim()
            $currentNetwork.Channel = $channelValue
        }
        elseif ($line -match "BSSID" -and $currentNetwork.SSID) {
            if (-not $currentNetwork.BSSIDs) {
                $currentNetwork.BSSIDs = @()
            }
            $bssid = ($line -split ":")[-1].Trim()
            if ($bssid -and $bssid.Length -gt 5) {
                $currentNetwork.BSSIDs += $bssid
                
                # Try to detect channel from BSSID scan
                if ($line -match "Channel\s*:\s*(\d+)") {
                    if (-not $currentNetwork.Channel) {
                        $currentNetwork.Channel = $matches[1]
                    }
                }
            }
        }
    }
    
    if ($currentNetwork.SSID) {
        $networks += $currentNetwork
    }
    
    # Display found networks with detailed info
    if ($networks.Count -gt 0) {
        Write-Host "${GREEN}[✓] تم العثور على $($networks.Count) شبكة WiFi${RESET}"
        Write-Host ""
        
        $networkIndex = 1
        $networks | ForEach-Object {
            $signalValue = $_.Signal
            if (-not $signalValue) { $signalValue = "---" }
            $channelValue = $_.Channel
            if (-not $channelValue) { $channelValue = "---" }
            
            # Color code signal strength
            $signalColor = $YELLOW
            if ($signalValue -match "100%") { $signalColor = $GREEN }
            elseif ($signalValue -match "7[5-9]%|8[0-9]%|9[0-9]%") { $signalColor = $GREEN }
            elseif ($signalValue -match "5[0-9]%|6[0-9]%|7[0-4]%") { $signalColor = $YELLOW }
            else { $signalColor = $RED }
            
            Write-Host "#$networkIndex - SSID: ${CYAN}$($_.SSID)${RESET}"
            Write-Host "   قوة الإشارة: ${signalColor}$signalValue${RESET}"
            Write-Host "   القناة: $channelValue"
            
            if ($_.BSSIDs -and $_.BSSIDs.Count -gt 0) {
                Write-Host "   BSSID: $($_.BSSIDs[0])"
                if ($_.BSSIDs.Count -gt 1) {
                    Write-Host "   BSSIDs إضافية: $($_.BSSIDs[1..($_.BSSIDs.Count-1)] -join ', ')"
                }
            }
            
            Write-Host ""
            $networkIndex++
        }
    }
    else {
        Write-Host "لم يتم العثور على شبكات WiFi"
    }
}
catch {
    Write-Host "${YELLOW}[*] تحتاج إلى تشغيل الكمبيوتر كمسؤول (Admin) لعرض شبكات WiFi بالكامل${RESET}"
}

Write-Host ""

# WiFi Channels Analysis
Write-Host "${CYAN}================ تحليل قنوات WiFi ==================${RESET}"
try {
    $wifiChannels = netsh wlan show all | Select-String "Channel"
    
    if ($wifiChannels) {
        Write-Host "${YELLOW}القنوات المستخدمة:${RESET}"
        $uniqueChannels = $wifiChannels -replace '.*Channel : ' -replace ' .*' | Select-Object -Unique
        Write-Host "$($uniqueChannels -join ', ')"
        Write-Host ""
        Write-Host "${YELLOW}التوصية:${RESET}"
        Write-Host "استخدم قنوات WiFi الخالية (1, 6, 11) لتجنب التداخل"
    }
}
catch {
    Write-Host "لم يتمكن من الوصول لمعلومات قنوات WiFi"
}

Write-Host ""

# Security Assessment & Recommendations
Write-Host "${CYAN}================ تقييم الأمان والتوصيات ===============${RESET}"
Write-Host ""

# Security Score System
$securityScore = 100
$securityIssues = @()

# Check for common security issues
try {
    # Check if WPS is mentioned (if found, it's a security risk)
    $wpsCheck = netsh wlan show interfaces | Select-String -Pattern "WPS|Protected Setup"
    if ($wpsCheck) {
        $securityScore -= 15
        $securityIssues += "❌ WPS مفعّل على الراوتر (خطر أماني)"
    }
}
catch {}

# Check connected device security
if ($deviceCount -gt 3) {
    $securityScore -= 10
    $securityIssues += "⚠️  عدد كبير من الأجهزة المتصلة ($deviceCount)"
}

# Display Security Score
Write-Host "${CYAN}درجة الأمان:${RESET} "
if ($securityScore -ge 80) {
    Write-Host "${GREEN}$securityScore/100 - ممتاز${RESET}"
}
elseif ($securityScore -ge 60) {
    Write-Host "${YELLOW}$securityScore/100 - جيد${RESET}"
}
else {
    Write-Host "${RED}$securityScore/100 - ضعيف${RESET}"
}

Write-Host ""

# Display Issues Found
if ($securityIssues.Count -gt 0) {
    Write-Host "${RED}المشاكل الأمنية المكتشفة:${RESET}"
    $securityIssues | ForEach-Object {
        Write-Host "  $_"
    }
    Write-Host ""
}

# Comprehensive Security Recommendations
Write-Host "${CYAN}التوصيات الأمنية الشاملة:${RESET}"
Write-Host ""

Write-Host "${YELLOW}إعدادات الراوتر:${RESET}"
Write-Host "  1. 🔐 تغيير كلمة مرور الـ Admin الافتراضية"
Write-Host "     → اذهب إلى 192.168.1.1 وسجل دخول باستخدام كلمة مرور قوية"
Write-Host ""
Write-Host "  2. 🛡️  تفعيل WPA2 أو WPA3 فقط"
Write-Host "     → عطّل WEP و TKIP و WPA القديم"
Write-Host ""
Write-Host "  3. ❌ عطّل WPS (WiFi Protected Setup)"
Write-Host "     → خطر أماني معروف يسهل اختراقه"
Write-Host ""
Write-Host "  4. 🔄 حدّث Firmware الراوتر"
Write-Host "     → تحقق من موقع المصنع للتحديثات الأمنية الأخيرة"
Write-Host ""
Write-Host "  5. 📡 غيّر اسم الشبكة (SSID)"
Write-Host "     → لا تستخدم SSID افتراضي يكشف نوع الراوتر"
Write-Host ""

Write-Host "${YELLOW}كلمات مرور WiFi:${RESET}"
Write-Host "  6. 🔑 استخدم كلمة مرور قوية جداً (16+ حرف)"
Write-Host "     → أحرف كبيرة + صغيرة + أرقام + رموز"
Write-Host ""
Write-Host "  7. 🔄 غيّر كلمة المرور كل 3-6 أشهر"
Write-Host "     → خاصة إذا تركت الراوتر عند الضيوف"
Write-Host ""

Write-Host "${YELLOW}المراقبة والصيانة:${RESET}"
Write-Host "  8. 👀 راقب الأجهزة المتصلة بانتظام"
Write-Host "     → ابحث عن أجهزة غير معروفة"
Write-Host ""
Write-Host "  9. 🚫 احظر الأجهزة المريبة"
Write-Host "     → استخدم MAC Filtering إذا لزم الأمر"
Write-Host ""

Write-Host "${YELLOW}إعدادات متقدمة:${RESET}"
Write-Host "  10. 🔒 فعّل WPA2/WPA3 Enterprise (للشركات)"
Write-Host "      → استخدم RADIUS server للمصادقة"
Write-Host ""
Write-Host "  11. 🌐 عطّل UPnP إذا لم تكن تحتاجه"
Write-Host "      → يمكن أن يسبب ثغرات أمنية"
Write-Host ""
Write-Host "  12. 📊 فعّل Registration Protocol على الراوتر"
Write-Host "      → للتحكم في الأجهزة الجديدة المتصلة"
Write-Host ""

Write-Host ""
Write-Host "${GREEN}✓ انتهى الفحص الأمني الشامل للشبكة.${RESET}"
Write-Host ""

# Export Report Option
Write-Host "${CYAN}نصيحة إضافية:${RESET}"
Write-Host "يمكنك حفظ هذا التقرير بتشغيل الأمر التالي:"
Write-Host ""
Write-Host "powershell -ExecutionPolicy Bypass -File `"$PSScriptRoot\router_security_audit.ps1`" | Out-File `"$PSScriptRoot\security_report.txt`""
Write-Host ""
