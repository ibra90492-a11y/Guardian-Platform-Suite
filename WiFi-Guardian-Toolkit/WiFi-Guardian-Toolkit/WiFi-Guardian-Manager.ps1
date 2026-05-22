# WiFi Guardian Toolkit - Master Manager
# مدير شامل لأدوات حماية شبكات WiFi

$ToolkitPath = $PSScriptRoot
$Version = "1.0.0"

function Show-MainMenu {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║                                                            ║" -ForegroundColor Cyan
    Write-Host "║     🛡️  WiFi Guardian Toolkit - نظام حماية الشبكات       ║" -ForegroundColor Cyan
    Write-Host "║                  إصدار $Version                             ║" -ForegroundColor Cyan
    Write-Host "║                                                            ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "الخيارات المتاحة:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  [1] 🔍 فحص أمان الشبكة الكامل" -ForegroundColor Green
    Write-Host "      اكتشف جميع الأجهزة والتهديدات"
    Write-Host ""
    Write-Host "  [2] 📊 إنشاء تقرير أمان شامل" -ForegroundColor Green
    Write-Host "      أنشئ تقرير HTML منسق وملون"
    Write-Host ""
    Write-Host "  [3] 📄 تحويل التقرير إلى PDF" -ForegroundColor Green
    Write-Host "      حول التقرير إلى PDF احترافي"
    Write-Host ""
    Write-Host "  [4] 📧 إرسال التقرير بالبريد" -ForegroundColor Green
    Write-Host "      أرسل التقرير إلى ibra90492@gmail.com"
    Write-Host ""
    Write-Host "  [5] 🚀 تنفيذ كامل (جميع الخيارات)" -ForegroundColor Green
    Write-Host "      فحص كامل + تقرير + PDF + بريد"
    Write-Host ""
    Write-Host "  [6] ⚙️  الإعدادات" -ForegroundColor Green
    Write-Host "      تخصيص بيانات البريد والإعدادات"
    Write-Host ""
    Write-Host "  [7] 📖 المساعدة والمعلومات" -ForegroundColor Green
    Write-Host "      اعرض معلومات الأداة والتعليمات"
    Write-Host ""
    Write-Host "  [0] ❌ خروج" -ForegroundColor Red
    Write-Host ""
}

function Run-FullSecurityAudit {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║  🔍 جاري تشغيل الفحص الأمني الكامل...   ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
    
    $auditScript = Join-Path $ToolkitPath "router_security_audit.ps1"
    
    if (Test-Path $auditScript) {
        & $auditScript
    }
    else {
        Write-Host "❌ لم يتم العثور على سكريبت الفحص" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "اضغط أي مفتاح للمتابعة..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Generate-Report {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║  📊 جاري إنشاء التقرير الشامل...        ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
    
    $reportScript = Join-Path $ToolkitPath "generate_security_report.ps1"
    
    if (Test-Path $reportScript) {
        & $reportScript -SendEmail:$false
    }
    else {
        Write-Host "❌ لم يتم العثور على سكريبت التقرير" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "اضغط أي مفتاح للمتابعة..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Convert-ToPDF {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║  📄 جاري تحويل التقرير إلى PDF...       ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
    
    $pdfScript = Join-Path $ToolkitPath "pdf_email_sender.ps1"
    
    if (Test-Path $pdfScript) {
        & $pdfScript -SendEmail:$false
    }
    else {
        Write-Host "❌ لم يتم العثور على سكريبت PDF" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "اضغط أي مفتاح للمتابعة..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Send-Email {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║  📧 جاري إرسال التقرير بالبريد...       ║" -ForegroundColor Yellow
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
    
    # بيانات البريد الهدف
    $toEmail = "ibra90492@gmail.com"
    
    Write-Host "البريد الإلكتروني للمستقبل: $toEmail" -ForegroundColor Cyan
    Write-Host ""
    
    # بيانات المرسل (يجب تحديثها)
    Write-Host "⚠️ ملاحظة مهمة:" -ForegroundColor Yellow
    Write-Host "لاستخدام وظيفة إرسال البريل، قم بـ:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. فعّل المصادقة الثنائية في حسابك على Gmail" -ForegroundColor Cyan
    Write-Host "2. أنشئ كلمة مرور تطبيق: https://myaccount.google.com/apppasswords" -ForegroundColor Cyan
    Write-Host "3. انسخ كلمة المرور وحدّث السكريبت" -ForegroundColor Cyan
    Write-Host ""
    
    $pdfScript = Join-Path $ToolkitPath "pdf_email_sender.ps1"
    
    if (Test-Path $pdfScript) {
        & $pdfScript -SendEmail -EmailAddress $toEmail
    }
    else {
        Write-Host "❌ لم يتم العثور على سكريبت البريد" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "اضغط أي مفتاح للمتابعة..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Run-FullProcess {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════╗" -ForegroundColor Magenta
    Write-Host "║  🚀 جاري تنفيذ العملية الكاملة...              ║" -ForegroundColor Magenta
    Write-Host "║     (فحص + تقرير + PDF + بريد)                  ║" -ForegroundColor Magenta
    Write-Host "╚════════════════════════════════════════════════════╝" -ForegroundColor Magenta
    Write-Host ""
    
    # الخطوة 1: الفحص الأمني
    Write-Host "[1/4] 🔍 الفحص الأمني الكامل..." -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    $auditScript = Join-Path $ToolkitPath "router_security_audit.ps1"
    if (Test-Path $auditScript) {
        & $auditScript
    }
    Write-Host ""
    
    # الخطوة 2: إنشاء التقرير
    Write-Host "[2/4] 📊 إنشاء التقرير HTML..." -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    $reportScript = Join-Path $ToolkitPath "generate_security_report.ps1"
    if (Test-Path $reportScript) {
        & $reportScript -SendEmail:$false
    }
    Start-Sleep -Seconds 2
    Write-Host ""
    
    # الخطوة 3: تحويل PDF
    Write-Host "[3/4] 📄 تحويل التقرير إلى PDF..." -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    $pdfScript = Join-Path $ToolkitPath "pdf_email_sender.ps1"
    if (Test-Path $pdfScript) {
        & $pdfScript -SendEmail:$false
    }
    Start-Sleep -Seconds 2
    Write-Host ""
    
    # الخطوة 4: إرسال البريد
    Write-Host "[4/4] 📧 إرسال التقرير بالبريل..." -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    if (Test-Path $pdfScript) {
        & $pdfScript -SendEmail -EmailAddress "ibra90492@gmail.com"
    }
    
    Write-Host ""
    Write-Host "✓ اكتملت جميع الخطوات بنجاح!" -ForegroundColor Green
    Write-Host ""
    Write-Host "اضغط أي مفتاح للمتابعة..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Show-Settings {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║             ⚙️  الإعدادات والتكوين               ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "الإعدادات الحالية:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📧 بيانات البريد الإلكتروني:" -ForegroundColor Cyan
    Write-Host "  المستقبل: ibra90492@gmail.com" -ForegroundColor Green
    Write-Host "  خادم SMTP: smtp.gmail.com" -ForegroundColor Green
    Write-Host "  المنفذ: 587" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "📁 مجلد الأدوات:" -ForegroundColor Cyan
    Write-Host "  $ToolkitPath" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "📄 الملفات المتاحة:" -ForegroundColor Cyan
    Write-Host "  ✓ router_security_audit.ps1 - فحص أمان الشبكة" -ForegroundColor Green
    Write-Host "  ✓ generate_security_report.ps1 - إنشاء التقرير" -ForegroundColor Green
    Write-Host "  ✓ pdf_email_sender.ps1 - تحويل وإرسال البريد" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "🔧 للتحديث والمساعدة:" -ForegroundColor Yellow
    Write-Host "  اتصل بـ: support@wifiguardian.local" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "اضغط أي مفتاح للعودة..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

function Show-Help {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║            📖 المساعدة والمعلومات                 ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "👋 مرحباً بك في WiFi Guardian Toolkit!" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "📋 ما هي هذه الأداة؟" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "WiFi Guardian هي أداة شاملة لفحص وحماية شبكات WiFi."
    Write-Host "تقدم:"
    Write-Host "  • فحص أمني متقدم لاكتشاف التهديدات"
    Write-Host "  • تقارير منسقة وملونة وجذابة"
    Write-Host "  • تحويل التقارير إلى PDF احترافية"
    Write-Host "  • إرسال التقارير مباشرة عبر البريد الإلكتروني"
    Write-Host ""
    
    Write-Host "🎯 الميزات الرئيسية:" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  ✓ كشف جميع الأجهزة المتصلة"
    Write-Host "  ✓ اكتشاف نظام التشغيل والموديل"
    Write-Host "  ✓ تحليل قوة الإشارة والقنوات"
    Write-Host "  ✓ درجة تقييم أمان الشبكة"
    Write-Host "  ✓ توصيات أمنية متقدمة"
    Write-Host "  ✓ تقارير ملونة وجذابة"
    Write-Host "  ✓ إرسال تلقائي بالبريل"
    Write-Host ""
    
    Write-Host "📚 كيفية الاستخدام:" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "1. اختر 'فحص أمان الشبكة الكامل' لبدء الفحص"
    Write-Host "2. اختر 'إنشاء تقرير' لإنشاء تقرير HTML"
    Write-Host "3. اختر 'تحويل إلى PDF' لتحويل التقرير"
    Write-Host "4. اختر 'إرسال البريد' لإرسال التقرير"
    Write-Host "5. أو استخدم 'تنفيذ كامل' للقيام بكل شيء"
    Write-Host ""
    
    Write-Host "📧 لاستخدام وظيفة البريل:" -ForegroundColor Yellow
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Yellow
    Write-Host "1. فعّل المصادقة الثنائية على حساب Gmail"
    Write-Host "2. أنشئ كلمة مرور تطبيق: https://myaccount.google.com/apppasswords"
    Write-Host "3. حدّث بيانات البريل في السكريبت"
    Write-Host ""
    
    Write-Host "❓ أسئلة متكررة:" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "س: هل الأداة آمنة؟"
    Write-Host "ج: نعم، الأداة توفر فقط معلومات عن شبكتك ولا تعدل أي إعدادات"
    Write-Host ""
    Write-Host "س: هل يمكن استخدام بريد إلكتروني آخر؟"
    Write-Host "ج: نعم، يمكنك تعديل البريد المستقبل في الإعدادات"
    Write-Host ""
    Write-Host "س: كم مرة يجب إجراء الفحص؟"
    Write-Host "ج: يفضل إجراء فحص شهري على الأقل"
    Write-Host ""
    
    Write-Host "🔗 روابط مفيدة:" -ForegroundColor Cyan
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "  • Gmail App Passwords: https://myaccount.google.com/apppasswords"
    Write-Host "  • WiFi Security Guide: https://security.google.com"
    Write-Host "  • Router Security: https://www.routersecurity.org"
    Write-Host ""
    
    Write-Host "اضغط أي مفتاح للعودة..." -ForegroundColor Cyan
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# ======================================
# حلقة البرنامج الرئيسية
# ======================================

Clear-Host

do {
    Show-MainMenu
    Write-Host "اختر رقم الخيار (0-7):" -ForegroundColor Yellow -NoNewline
    Write-Host " "
    $choice = Read-Host
    
    Clear-Host
    
    switch ($choice) {
        "1" { Run-FullSecurityAudit }
        "2" { Generate-Report }
        "3" { Convert-ToPDF }
        "4" { Send-Email }
        "5" { Run-FullProcess }
        "6" { Show-Settings }
        "7" { Show-Help }
        "0" { 
            Write-Host ""
            Write-Host "شكراً لاستخدام WiFi Guardian Toolkit! 👋" -ForegroundColor Green
            Write-Host ""
            exit 0
        }
        default { 
            Write-Host "❌ خيار غير صحيح! يرجى اختيار من 0 إلى 7" -ForegroundColor Red
            Write-Host ""
            Start-Sleep -Seconds 2
        }
    }
} while ($true)
