@echo off
chcp 65001 > nul
color 0A
cls

echo.
echo ═══════════════════════════════════════════════════════════════════
echo   WiFi Guardian Toolkit - Launcher
echo ═══════════════════════════════════════════════════════════════════
echo.
echo 1️⃣  Main CLI (يوصى به)
echo 2️⃣  Kali Setup Wizard مباشرة
echo 3️⃣  Linux Terminal مباشرة (wt + kali)
echo 4️⃣  فتح Kali بـ Ctrl+Shift+5 (محاكاة تلقائية)
echo 5️⃣  Open Main App (GUI) + Kali Terminal
echo 6️⃣  خروج
echo.
echo ═══════════════════════════════════════════════════════════════════
echo.

set /p choice="اختر خيار (1-6): "

if "%choice%"=="1" (
    py main.py
) else if "%choice%"=="2" (
    powershell -NoExit -Command "py main.py; Write-Host ''; Write-Host 'اختر الخيار 6 داخل البرنامج لتشغيل معالج Kali/WSL'"
) else if "%choice%"=="3" (
    powershell -NoExit -Command "wt wsl.exe -d kali-linux bash"
) else if "%choice%"=="4" (
    echo.
    echo ⚠️  تنبيه: تأكد من أن نافذة Windows Terminal مفتوحة وفي المقدمة!
    echo     سيتم إرسال الاختصار Ctrl+Shift+5 بعد 3 ثوانٍ...
    echo.
    timeout /t 3 >nul
    py -c "import pyautogui; pyautogui.hotkey('ctrl', 'shift', '5'); print('✅ تم إرسال الاختصار!')"
    echo.
) else if "%choice%"=="5" (
    start "kali-linux" powershell -NoProfile -Command "wt wsl.exe -d kali-linux bash"
    timeout /t 2 >nul
    py main.py
) else if "%choice%"=="6" (
    exit /b 0
) else (
    echo ❌ اختيار غير صحيح!
)

echo.
echo ═══════════════════════════════════════════════════════════════════
pause