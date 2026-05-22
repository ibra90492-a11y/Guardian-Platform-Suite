# WiFi Guardian Toolkit - Quick Start & Installation
# سكريبت البدء السريع والتثبيت

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🛡️  WiFi Guardian - بدء سريع وتثبيت            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# معلومات النظام
$ScriptPath = $PSScriptRoot
$OSVersion = [System.Environment]::OSVersion.VersionString
$PowerShellVersion = $PSVersionTable.PSVersion.Major

Write-Host "معلومات النظام:" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host "  نظام التشغيل: $OSVersion"
Write-Host "  إصدار PowerShell: $PowerShellVersion"
Write-Host "  المسار: $ScriptPath"
Write-Host ""

# التحقق من المتطلبات
Write-Host "التحقق من المتطلبات..." -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow

$requirements = @()
$allMet = $true

# تحقق من PowerShell 5.0+
if ($PowerShellVersion -ge 5) {
    Write-Host "✓ PowerShell 5.0+ متوافق" -ForegroundColor Green
    $requirements += @{Name = "PowerShell"; Status = "OK" }
}
else {
    Write-Host "❌ PowerShell 5.0+ مطلوب (لديك: $PowerShellVersion)" -ForegroundColor Red
    $allMet = $false
}

# تحقق من Windows 10+
if ([System.Environment]::OSVersion.Platform -eq "Win32NT" -and 
    [System.Environment]::OSVersion.Version.Major -ge 10) {
    Write-Host "✓ Windows 10+ متوافق" -ForegroundColor Green
    $requirements += @{Name = "Windows"; Status = "OK" }
}
else {
    Write-Host "⚠️ يفضل Windows 10 أو أحدث" -ForegroundColor Yellow
}

# تحقق من الملفات المطلوبة
Write-Host ""
Write-Host "التحقق من الملفات:" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow

$requiredFiles = @(
    "WiFi-Guardian-Manager.ps1",
    "router_security_audit.ps1",
    "generate_security_report.ps1",
    "pdf_email_sender.ps1",
    "README.md",
    "config.json"
)

foreach ($file in $requiredFiles) {
    $filePath = Join-Path $ScriptPath $file
    if (Test-Path $filePath) {
        Write-Host "✓ $file موجود" -ForegroundColor Green
    }
    else {
        Write-Host "❌ $file غير موجود" -ForegroundColor Red
        $allMet = $false
    }
}

Write-Host ""

# إذا كانت جميع المتطلبات مستوفاة
if ($allMet) {
    Write-Host "✓ جميع المتطلبات مستوفاة!" -ForegroundColor Green
    Write-Host ""
}
else {
    Write-Host "⚠️ بعض المتطلبات غير مستوفاة" -ForegroundColor Yellow
    Write-Host ""
}

# خيارات البدء
Write-Host "الخيارات المتاحة:" -ForegroundColor Yellow
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
Write-Host ""
Write-Host "  [1] 🚀 تشغيل مدير WiFi Guardian" -ForegroundColor Green
Write-Host "  [2] 🔍 تشغيل الفحص الأمني فقط" -ForegroundColor Green
Write-Host "  [3] 📊 إنشاء تقرير فقط" -ForegroundColor Green
Write-Host "  [4] 📖 اعرض ملف README" -ForegroundColor Green
Write-Host "  [5] ⚙️  اعرض الإعدادات" -ForegroundColor Green
Write-Host "  [6] 🔧 إنشاء اختصارات سريعة" -ForegroundColor Green
Write-Host "  [0] ❌ خروج" -ForegroundColor Red
Write-Host ""

$choice = Read-Host "اختر خياراً (0-6)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "جاري تشغيل WiFi Guardian Manager..." -ForegroundColor Cyan
        Write-Host ""
        & (Join-Path $ScriptPath "WiFi-Guardian-Manager.ps1")
    }
    
    "2" {
        Write-Host ""
        Write-Host "جاري تشغيل الفحص الأمني..." -ForegroundColor Cyan
        Write-Host ""
        & (Join-Path $ScriptPath "router_security_audit.ps1")
    }
    
    "3" {
        Write-Host ""
        Write-Host "جاري إنشاء التقرير..." -ForegroundColor Cyan
        Write-Host ""
        & (Join-Path $ScriptPath "generate_security_report.ps1") -SendEmail:$false
    }
    
    "4" {
        Write-Host ""
        Write-Host "فتح ملف README..." -ForegroundColor Cyan
        Write-Host ""
        $readmePath = Join-Path $ScriptPath "README.md"
        if (Test-Path $readmePath) {
            Start-Process $readmePath
        }
        else {
            Write-Host "❌ لم يتم العثور على ملف README" -ForegroundColor Red
        }
    }
    
    "5" {
        Write-Host ""
        Write-Host "فتح ملف الإعدادات..." -ForegroundColor Cyan
        Write-Host ""
        $configPath = Join-Path $ScriptPath "config.json"
        if (Test-Path $configPath) {
            Get-Content $configPath | ConvertFrom-Json | Format-List | Out-Host
        }
        else {
            Write-Host "❌ لم يتم العثور على ملف الإعدادات" -ForegroundColor Red
        }
    }
    
    "6" {
        Write-Host ""
        Write-Host "إنشاء اختصارات سريعة..." -ForegroundColor Cyan
        Write-Host ""
        
        # إنشاء اختصار على سطح المكتب
        $desktopPath = [Environment]::GetFolderPath([Environment+SpecialFolder]::Desktop)
        $shortcutPath = Join-Path $desktopPath "WiFi Guardian.lnk"
        
        $WshShell = New-Object -ComObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut($shortcutPath)
        $Shortcut.TargetPath = "powershell.exe"
        $Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$ScriptPath\WiFi-Guardian-Manager.ps1`""
        $Shortcut.WorkingDirectory = $ScriptPath
        $Shortcut.Description = "WiFi Guardian - نظام حماية الشبكات"
        $Shortcut.IconLocation = "powershell.exe"
        $Shortcut.Save()
        
        Write-Host "✓ تم إنشاء اختصار على سطح المكتب" -ForegroundColor Green
        Write-Host "  المسار: $shortcutPath" -ForegroundColor Cyan
        Write-Host ""
        
        # إنشاء اختصار في قائمة البداية
        $startMenuPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
        $toolkitShortcut = Join-Path $startMenuPath "WiFi Guardian.lnk"
        
        $StartMenuShortcut = $WshShell.CreateShortcut($toolkitShortcut)
        $StartMenuShortcut.TargetPath = "powershell.exe"
        $StartMenuShortcut.Arguments = "-ExecutionPolicy Bypass -File `"$ScriptPath\WiFi-Guardian-Manager.ps1`""
        $StartMenuShortcut.WorkingDirectory = $ScriptPath
        $StartMenuShortcut.Description = "WiFi Guardian - نظام حماية الشبكات"
        $StartMenuShortcut.Save()
        
        Write-Host "✓ تم إنشاء اختصار في قائمة البداية" -ForegroundColor Green
        Write-Host "  المسار: $toolkitShortcut" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "الآن يمكنك الوصول إلى WiFi Guardian بسهولة!" -ForegroundColor Green
    }
    
    "0" {
        Write-Host ""
        Write-Host "شكراً لاستخدام WiFi Guardian! 👋" -ForegroundColor Green
        Write-Host ""
        exit 0
    }
    
    default {
        Write-Host ""
        Write-Host "❌ خيار غير صحيح!" -ForegroundColor Red
        Write-Host ""
    }
}

Write-Host ""
Write-Host "اضغط أي مفتاح للخروج..." -ForegroundColor Cyan
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
