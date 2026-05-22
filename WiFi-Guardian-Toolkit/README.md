# WiFi Guardian Toolkit

أداة Windows بواجهة رسومية مبنية بـ Tkinter لإدارة جلسة Kali عبر WSL، وعرض معلومات الاتصال، وتشغيل أدوات Kali من داخل التطبيق.

---

## الحالة الحالية

- الواجهة الرئيسية GUI وليست CLI.
- يتم فتح جلسة Kali في الخلفية عند تشغيل البرنامج.
- أوامر Kali التي تحتاج صلاحيات تعمل عبر مسار موحد داخل WSL.
- حساب Kali المحفوظ في التطبيق يمكن مزامنته مع حساب Kali الحقيقي داخل WSL.

---

## تشغيل البرنامج

```bash
python main.py
```

يمكنك أيضاً التشغيل عبر:

- `run.bat`
- اختصار سطح المكتب إذا تم إنشاؤه مسبقاً

---

## الواجهة الرئيسية

القائمة اليسرى تحتوي على:

1. `Settings / الإعدادات`
2. `Tools / الأدوات`
3. `Prevent Tracking / منع التتبع`
4. `Contact Information / معلومات الاتصال`

اللوحة اليمنى تعرض:

- `SSID`
- `PassWord`
- `InterFace`
- `IP-Address`
- `DNS (DoH)`
- `DNS (DoT)`
- `DNS (WARP)`
- `State`

كما تعرض في الأعلى حالة الاتصال:

- `Contact Details: Contact is not secure`
- `Contact Details: Contact is secure`

---

## Prevent Tracking

عند الضغط على زر `Prevent Tracking`:

- لا يتم فتح نافذة Kali جديدة.
- يتم تفعيل حالة الحماية داخل التطبيق فقط.
- يتم تحديث `IP-Address` و`State` من الملف `dummy_ip_country.csv`.
- يتم تبديل `IP-Address` و`State` كل 3 دقائق أثناء بقاء الحماية مفعلة.
- تتحول القيم التالية إلى `Yes`:
  - `DNS (DoH)`
  - `DNS (DoT)`
  - `DNS (WARP)`

عند عدم التفعيل:

- `IP-Address` يعرض `Real Wi-Fi network IP number`
- قيم DNS تعرض `No`
- `State` يعرض `Saudi Arabia`

---

## Kali Account و WSL

التطبيق يستخدم الملف `kali_account.txt` لتخزين:

- اسم المستخدم
- كلمة المرور
- الاسم الكامل

وعند وجود حساب محفوظ، يقوم التطبيق بمزامنته مع Kali داخل WSL بحيث:

- يتم إنشاء المستخدم إذا لم يكن موجوداً
- يتم تحديث كلمة المرور إذا كان موجوداً
- يتم ضبط المستخدم الافتراضي لجلسات WSL الجديدة

هذا يحل مشكلة التناقض بين الحساب المحفوظ في التطبيق والحساب الحقيقي داخل Kali.

---

## الإعدادات

داخل `Settings / الإعدادات` ستجد:

1. `Show Wifi password`
2. `Change the software security code`
3. `Installation Requirements`
4. `Kali Linux Account`
5. `Sync Kali Account With WSL`
6. `I forgot my username or password for my Kali Linux account`

### زر Sync Kali Account With WSL

هذا الزر ينفذ مزامنة يدوية مباشرة بين البيانات الموجودة في `kali_account.txt` وبين Kali داخل WSL.

استخدمه عندما:

- تغيّر كلمة المرور داخل التطبيق
- تغيّر الحساب في الملف
- تريد إعادة تطبيق الحساب على WSL
- تريد إصلاح مشكلة عدم قبول بيانات دخول Kali

---

## Tools Panel

لوحة الأدوات تعرض فئات أدوات Kali في واجهة 3 أعمدة، وتشمل:

- Network & Recon
- Password & Auth
- Web App Testing
- Wireless & RF
- Forensics
- Privacy & Proxy

التنفيذ يتم عبر مسار موحد داخل WSL:

- الأدوات العادية تعمل كمستخدم Kali
- الأدوات التي تحتاج صلاحيات تعمل كمستخدم root داخل WSL

بدون فتح طرفيات إضافية لكل أمر.

---

## Installation Requirements

زر `Installation Requirements` يثبت الأدوات الأساسية داخل Kali عبر WSL، مثل:

- `nmap`
- `masscan`
- `tcpdump`
- `aircrack-ng`
- `wifite`
- `reaver`
- `john`
- `hashcat`
- `hydra`
- `sqlmap`
- `nikto`
- `gobuster`
- `whatweb`
- `wpscan`
- `medusa`
- `binwalk`
- `foremost`
- `volatility3` عند توفره

---

## الملفات المهمة

- `main.py`: التطبيق الرئيسي
- `kali_account.txt`: بيانات حساب Kali المحفوظة
- `dummy_ip_country.csv`: بيانات IP/State المستخدمة عند تفعيل الحماية
- `security_code.txt`: رمز حماية البرنامج
- `installation_requirements.ps1`: ملف تثبيت مساعد
- `run.bat`: ملف تشغيل سريع

---

## المتطلبات

- Windows
- Python 3.10+
- WSL
- توزيعة Kali Linux داخل WSL

لتثبيت المكتبات:

```bash
pip install -r requirements.txt
```

لتثبيت WSL وKali عند الحاجة:

```powershell
wsl --install
wsl --install -d kali-linux
```

---

## ملاحظات مهمة

- بعض أوامر الأدوات تتطلب أن تكون الحزم مثبتة فعلياً داخل Kali.
- إذا كان حساب Kali غير متزامن، استخدم زر `Sync Kali Account With WSL`.
- إذا لم تكن توزيعة Kali مثبتة، فلن تعمل ميزات WSL.
- بعض عمليات التثبيت قد تستغرق وقتاً بحسب سرعة الشبكة.

---

## الاستخدام الأخلاقي

راجع الملف:

- [ETHICAL_USE.md](ETHICAL_USE.md)

واستخدم الأدوات فقط على الأنظمة أو الشبكات التي لديك تصريح قانوني للعمل عليها.