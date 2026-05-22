"""
سكريبت فحص المواقع الشامل
يقوم بفحص جميع الثغرات المطلوبة تلقائياً
"""

import subprocess
import re
import ssl
import socket
import requests
import httpx
from datetime import datetime
from urllib.parse import urlparse
from typing import Dict, List, Optional
import json

from backend.security.policy import normalize_url, validate_authorized_target


SECURITY_HEADERS = {
    "strict-transport-security": "HTTP Strict Transport Security",
    "content-security-policy": "Content Security Policy",
    "x-frame-options": "Clickjacking protection",
    "x-content-type-options": "MIME sniffing protection",
    "referrer-policy": "Referrer privacy policy",
    "permissions-policy": "Browser permissions policy",
}


async def scan_security_headers(target: str) -> dict:
    policy = validate_authorized_target(target)
    if not policy.allowed:
        return {"status": "blocked", "message": policy.reason, "findings": []}

    url = normalize_url(target)
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            response = await client.get(url)
    except httpx.HTTPError as exc:
        return {"status": "error", "message": str(exc), "findings": []}

    headers = {key.lower(): value for key, value in response.headers.items()}
    findings = []
    for header, label in SECURITY_HEADERS.items():
        present = header in headers
        findings.append(
            {
                "name": label,
                "header": header,
                "present": present,
                "severity": "info" if present else "medium",
                "recommendation": "Present" if present else f"Add the {header} response header.",
            }
        )

    missing = [item for item in findings if not item["present"]]
    risk_score = min(100, 20 + len(missing) * 10)
    return {
        "status": "success",
        "target": str(response.url),
        "http_status": response.status_code,
        "server": response.headers.get("server", "unknown"),
        "risk_score": risk_score,
        "findings": findings,
    }


class WebSecurityScanner:
    """
    ماسح المواقع الأمني الشامل
    يفحص: SSL, رؤوس الأمان, ملفات حساسة, ثغرات, منافذ, إلخ
    """
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.parsed_url = urlparse(target_url)
        self.domain = self.parsed_url.netloc or self.parsed_url.path
        self.base_url = f"{self.parsed_url.scheme}://{self.domain}"
        self.results = {}
        
    def scan_all(self, progress_callback=None):
        """يقوم بجميع الفحوصات"""
        
        checks = [
            ("فحص رؤوس الأمان", self.check_security_headers),
            ("فحص SSL/TLS", self.check_ssl_tls),
            ("فحص الملفات الحساسة", self.check_sensitive_files),
            ("فحص المنافذ المفتوحة", self.check_open_ports),
            ("فحص SQL Injection", self.check_sql_injection),
            ("فحص XSS", self.check_xss),
            ("فحص IDOR", self.check_idor),
            ("فحص المصادقة", self.check_authentication),
            ("فحص معلومات الخادم", self.check_server_info),
            ("فحص DNS و Subdomains", self.check_dns),
            ("فحص رفع الملفات", self.check_file_upload),
            ("فحص CSRF", self.check_csrf),
        ]
        
        total = len(checks)
        for i, (name, check_func) in enumerate(checks):
            if progress_callback:
                progress_callback(int((i/total)*100), f"جاري {name}...")
            try:
                result = check_func()
                self.results[check_func.__name__.replace('check_', '')] = result
            except Exception as e:
                self.results[check_func.__name__.replace('check_', '')] = {"error": str(e)}
        
        # حساب درجة المخاطر
        self.results['risk_score'] = self.calculate_risk_score()
        
        # إنشاء التوصيات
        self.results['recommendations'] = self.generate_recommendations()
        
        if progress_callback:
            progress_callback(100, "اكتمل الفحص بنجاح!")
        
        return self.results
    
    def check_security_headers(self) -> Dict:
        """فحص رؤوس الأمان"""
        headers = {}
        try:
            response = requests.get(self.base_url, timeout=10, verify=False)
            headers = dict(response.headers)
        except:
            pass
        
        critical_headers = {
            'strict-transport-security': {'present': False, 'critical': True},
            'content-security-policy': {'present': False, 'critical': True},
            'x-frame-options': {'present': False, 'critical': False},
            'x-content-type-options': {'present': False, 'critical': False},
            'referrer-policy': {'present': False, 'critical': False},
            'permissions-policy': {'present': False, 'critical': False},
        }
        
        for header in critical_headers:
            if header in headers:
                critical_headers[header]['present'] = True
        
        return {
            'headers': headers,
            'critical_headers': critical_headers,
            'missing_critical': [h for h, v in critical_headers.items() if v['critical'] and not v['present']]
        }
    
    def check_ssl_tls(self) -> Dict:
        """فحص SSL/TLS"""
        result = {
            'valid': False,
            'expiry_date': None,
            'cipher_strength': 'unknown',
            'tls_support': False,
            'heartbleed': False
        }
        
        try:
            context = ssl.create_default_context()
            with socket.create_connection((self.domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.domain) as ssock:
                    cert = ssock.getpeercert()
                    result['valid'] = True
                    result['expiry_date'] = cert.get('notAfter')
                    
                    # فحص قوة التشفير
                    cipher = ssock.cipher()
                    result['cipher_strength'] = cipher[2] if cipher else 'unknown'
                    result['tls_support'] = ssock.version() in ['TLSv1.2', 'TLSv1.3']
        except:
            pass
        
        # فحص Heartbleed باستخدام nmap
        try:
            cmd = f"nmap --script ssl-heartbleed -p 443 {self.domain} 2>/dev/null | grep -i vulnerable"
            result_heartbleed = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            result['heartbleed'] = 'VULNERABLE' in result_heartbleed.stdout.upper()
        except:
            pass
        
        return result
    
    def check_sensitive_files(self) -> List[Dict]:
        """فحص الملفات الحساسة"""
        sensitive_paths = [
            {'path': '/.git/', 'critical': True, 'description': 'قد يحتوي على كود المصدر الكامل'},
            {'path': '/.env', 'critical': True, 'description': 'قد يحتوي على مفاتيح API وكلمات مرور'},
            {'path': '/wp-config.php', 'critical': True, 'description': 'بيانات اتصال WordPress'},
            {'path': '/config.php', 'critical': True, 'description': 'ملف تكوين PHP'},
            {'path': '/robots.txt', 'critical': False, 'description': 'قد يكشف مسارات مخفية'},
            {'path': '/.htaccess', 'critical': False, 'description': 'قواعد الخادم'},
            {'path': '/backup/', 'critical': True, 'description': 'نسخ احتياطية'},
            {'path': '/backup.sql', 'critical': True, 'description': 'نسخة قاعدة البيانات'},
            {'path': '/debug.log', 'critical': False, 'description': 'سجلات التصحيح'},
            {'path': '/phpinfo.php', 'critical': True, 'description': 'معلومات PHP'},
            {'path': '/admin/', 'critical': False, 'description': 'واجهة إدارة ظاهرة'},
            {'path': '/.aws/credentials', 'critical': True, 'description': 'مفاتيح AWS'},
            {'path': '/.ssh/id_rsa', 'critical': True, 'description': 'مفتاح SSH الخاص'},
        ]
        
        found = []
        for item in sensitive_paths:
            try:
                url = f"{self.base_url}{item['path']}"
                response = requests.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    found.append({
                        'path': item['path'],
                        'critical': item['critical'],
                        'severity': 'عالية جداً' if item['critical'] else 'متوسطة',
                        'description': item['description'],
                        'status_code': response.status_code
                    })
                elif response.status_code == 403:
                    found.append({
                        'path': item['path'],
                        'critical': item['critical'],
                        'severity': 'متوسطة',
                        'description': f"{item['description']} (محمي بـ 403 - قد يكون قابلاً للاختراق)",
                        'status_code': response.status_code
                    })
            except:
                pass
        
        return found
    
    def check_open_ports(self) -> List[Dict]:
        """فحص المنافذ المفتوحة"""
        dangerous_ports = {
            21: 'FTP (غير مشفر)',
            22: 'SSH',
            23: 'Telnet (خطير جداً)',
            25: 'SMTP',
            80: 'HTTP',
            443: 'HTTPS',
            3306: 'MySQL',
            5432: 'PostgreSQL',
            6379: 'Redis',
            27017: 'MongoDB',
            9200: 'Elasticsearch',
            8080: 'HTTP Alt',
            8443: 'HTTPS Alt',
        }
        
        open_ports = []
        try:
            cmd = f"nmap -sS -sV --top-ports 100 {self.domain} 2>/dev/null | grep open"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            for line in result.stdout.split('\\n'):
                if '/tcp' in line or '/udp' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        port_str = parts[0].split('/')[0]
                        try:
                            port = int(port_str)
                            service = dangerous_ports.get(port, parts[1] if len(parts) > 1 else 'unknown')
                            open_ports.append({'port': port, 'service': service})
                        except:
                            pass
        except:
            pass
        
        return open_ports
    
    def check_sql_injection(self) -> Dict:
        """فحص ثغرات SQL Injection"""
        result = {'vulnerable': False, 'vulnerable_params': [], 'tested_params': []}
        
        # نقاط الضعف المحتملة
        test_params = ['id', 'page', 'user', 'product', 'cat', 'category', 'post']
        payloads = ["'", "' OR '1'='1", "1' AND '1'='1", "1' OR '1'='1'--"]
        
        for param in test_params:
            for payload in payloads:
                try:
                    test_url = f"{self.base_url}?{param}={payload}"
                    response = requests.get(test_url, timeout=5, verify=False)
                    result['tested_params'].append(param)
                    
                    # علامات وجود ثغرة SQL
                    sql_errors = [
                        'sql syntax', 'mysql_fetch', 'ora-', 'odbc', 'sqlite',
                        'unclosed quotation', 'microsoft ole db', 'division by zero'
                    ]
                    
                    for error in sql_errors:
                        if error.lower() in response.text.lower():
                            result['vulnerable'] = True
                            result['vulnerable_params'].append(param)
                            result['evidence'] = f"ظهر خطأ SQL: {error}"
                            break
                except:
                    pass
        
        return result
    
    def check_xss(self) -> Dict:
        """فحص ثغرات XSS"""
        result = {'vulnerable': False, 'vulnerable_params': [], 'type': None}
        
        test_params = ['search', 'q', 's', 'query', 'name', 'id']
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "'><script>alert(1)</script>",
            "\\\"><script>alert(1)</script>"
        ]
        
        for param in test_params:
            for payload in payloads:
                try:
                    test_url = f"{self.base_url}?{param}={payload}"
                    response = requests.get(test_url, timeout=5, verify=False)
                    
                    if payload in response.text:
                        result['vulnerable'] = True
                        result['vulnerable_params'].append(param)
                        result['type'] = 'Reflected XSS'
                        break
                except:
                    pass
        
        return result
    
    def check_idor(self) -> Dict:
        """فحص ثغرات IDOR"""
        result = {'vulnerable': False, 'vulnerable_paths': []}
        
        # مسارات IDOR المحتملة
        idor_paths = [
            '/user/profile?id=1',
            '/profile.php?id=1',
            '/invoice/1',
            '/order/1',
            '/user/1',
            '/account?id=1',
        ]
        
        for path in idor_paths:
            try:
                url = f"{self.base_url}{path}"
                response1 = requests.get(url, timeout=5, verify=False)
                
                # محاولة تغيير المعرف
                if '1' in path:
                    path2 = path.replace('1', '2')
                    url2 = f"{self.base_url}{path2}"
                    response2 = requests.get(url2, timeout=5, verify=False)
                    
                    if response1.status_code == 200 and response2.status_code == 200:
                        if response1.text != response2.text:
                            result['vulnerable'] = True
                            result['vulnerable_paths'].append(path)
            except:
                pass
        
        return result
    
    def check_authentication(self) -> Dict:
        """فحص نقاط الضعف في المصادقة"""
        result = {
            'has_rate_limit': False,
            'weak_password_allowed': False,
            'has_mfa': False,
            'safe_error_messages': False
        }
        
        # فحص حد محاولات الدخول
        login_url = f"{self.base_url}/login"
        test_payloads = [
            {'username': 'admin', 'password': 'wrong1'},
            {'username': 'admin', 'password': 'wrong2'},
            {'username': 'admin', 'password': 'wrong3'},
            {'username': 'admin', 'password': 'wrong4'},
            {'username': 'admin', 'password': 'wrong5'},
        ]
        
        similar_responses = []
        for payload in test_payloads:
            try:
                response = requests.post(login_url, data=payload, timeout=5, verify=False)
                similar_responses.append(response.text[:200])
            except:
                pass
        
        # إذا كانت جميع الردود متشابهة، لا يوجد حد للمحاولات
        if len(set(similar_responses)) == 1 and len(similar_responses) > 3:
            result['has_rate_limit'] = False
        else:
            result['has_rate_limit'] = True
        
        # فحص كلمات المرور الضعيفة
        weak_passwords = ['123456', 'password', 'admin123', 'qwerty', '123456789']
        for weak in weak_passwords:
            try:
                response = requests.post(login_url, data={'username': 'admin', 'password': weak}, timeout=5, verify=False)
                if 'success' in response.text.lower() or 'welcome' in response.text.lower():
                    result['weak_password_allowed'] = True
                    break
            except:
                pass
        
        # فحص رسائل الخطأ
        try:
            response = requests.post(login_url, data={'username': 'nonexistent_user_12345', 'password': 'wrong'}, timeout=5, verify=False)
            if 'user not found' in response.text.lower() or 'does not exist' in response.text.lower():
                result['safe_error_messages'] = False
            else:
                result['safe_error_messages'] = True
        except:
            pass
        
        return result
    
    def check_server_info(self) -> Dict:
        """فحص معلومات الخادم"""
        result = {
            'server': 'unknown',
            'php_version': 'unknown',
            'framework': 'unknown',
            'cms': 'unknown',
            'has_waf': False
        }
        
        try:
            response = requests.get(self.base_url, timeout=10, verify=False)
            
            # خادم الويب
            if 'Server' in response.headers:
                result['server'] = response.headers['Server']
            
            # PHP version
            php_patterns = [r'X-Powered-By: PHP/(\\d+\\.\\d+\\.\\d+)', r'PHP/(\\d+\\.\\d+\\.\\d+)']
            for pattern in php_patterns:
                match = re.search(pattern, str(response.headers))
                if match:
                    result['php_version'] = match.group(1)
                    break
            
            # CMS detection
            cms_signatures = {
                'wp-content': 'WordPress',
                'wp-includes': 'WordPress',
                'Joomla': 'Joomla',
                'Drupal': 'Drupal',
                'laravel': 'Laravel',
                'django': 'Django',
                'rails': 'Ruby on Rails'
            }
            
            for sig, cms in cms_signatures.items():
                if sig.lower() in response.text.lower():
                    result['cms'] = cms
                    result['framework'] = cms
                    break
            
            # WAF detection
            waf_headers = ['x-sucuri-id', 'x-cdn', 'cf-ray', 'x-waf', 'akamai']
            for header in waf_headers:
                if header in response.headers:
                    result['has_waf'] = True
                    break
                    
        except:
            pass
        
        return result
    
    def check_dns(self) -> Dict:
        """فحص DNS و Subdomains"""
        result = {
            'subdomains': [],
            'zone_transfer_vulnerable': False,
            'records': {}
        }
        
        # فحص Zone Transfer
        try:
            cmd = f"dig axfr @8.8.8.8 {self.domain} 2>/dev/null | grep -c 'ANSWER SECTION'"
            zone_result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if int(zone_result.stdout.strip() or '0') > 0:
                result['zone_transfer_vulnerable'] = True
        except:
            pass
        
        # فحص Subdomains شائعة
        common_subdomains = [
            'www', 'mail', 'ftp', 'admin', 'blog', 'shop', 'api', 'dev',
            'test', 'staging', 'dashboard', 'app', 'portal', 'cpanel'
        ]
        
        for sub in common_subdomains:
            try:
                subdomain = f"{sub}.{self.domain}"
                socket.gethostbyname(subdomain)
                result['subdomains'].append(subdomain)
            except:
                pass
        
        return result
    
    def check_file_upload(self) -> Dict:
        """فحص ثغرات رفع الملفات"""
        result = {'vulnerable': False, 'dangerous_types': []}
        
        # مسارات رفع الملفات المحتملة
        upload_paths = ['/upload', '/uploads', '/file/upload', '/api/upload', '/image/upload']
        
        dangerous_extensions = ['.php', '.asp', '.jsp', '.aspx', '.cgi', '.pl', '.py']
        
        for path in upload_paths:
            try:
                url = f"{self.base_url}{path}"
                response = requests.get(url, timeout=5, verify=False)
                if response.status_code == 200:
                    # فحص إذا كان هناك أي إشارة لرفع ملفات
                    if 'upload' in response.text.lower() or 'file' in response.text.lower():
                        result['vulnerable'] = True
                        result['dangerous_types'].extend(dangerous_extensions)
            except:
                pass
        
        return result
    
    def check_csrf(self) -> Dict:
        """فحص ثغرات CSRF"""
        result = {'vulnerable': False, 'forms_without_token': []}
        
        try:
            response = requests.get(self.base_url, timeout=10, verify=False)
            
            # البحث عن النماذج
            form_pattern = r'<form[^>]*>.*?</form>'
            forms = re.findall(form_pattern, response.text, re.DOTALL | re.IGNORECASE)
            
            for form in forms:
                has_csrf = False
                csrf_patterns = ['csrf', 'token', '_token', 'authenticity_token']
                
                for pattern in csrf_patterns:
                    if pattern in form.lower():
                        has_csrf = True
                        break
                
                if not has_csrf:
                    result['vulnerable'] = True
                    # لا نضيف النموذج نفسه لتجنب التكرار
                    if len(result['forms_without_token']) < 10:
                        result['forms_without_token'].append('نموذج بدون CSRF token')
        except:
            pass
        
        return result
    
    def calculate_risk_score(self) -> int:
        """حساب درجة المخاطر الإجمالية"""
        score = 0
        
        # رؤوس الأمان
        security_headers = self.results.get('security_headers', {})
        missing_critical = security_headers.get('missing_critical', [])
        score += len(missing_critical) * 10
        
        # SSL
        ssl = self.results.get('ssl_tls', {})
        if not ssl.get('valid'):
            score += 15
        if ssl.get('heartbleed'):
            score += 20
        if not ssl.get('tls_support'):
            score += 10
        
        # الملفات الحساسة
        sensitive_files = self.results.get('sensitive_files', [])
        for file in sensitive_files:
            if file.get('critical'):
                score += 15
            else:
                score += 5
        
        # المنافذ المفتوحة
        open_ports = self.results.get('open_ports', [])
        dangerous_ports_list = [21, 23, 3306, 5432, 6379, 27017, 9200]
        for port in open_ports:
            if port['port'] in dangerous_ports_list:
                score += 10
        
        # SQL Injection
        sql = self.results.get('sql_injection', {})
        if sql.get('vulnerable'):
            score += 25
        
        # XSS
        xss = self.results.get('xss', {})
        if xss.get('vulnerable'):
            score += 20
        
        # IDOR
        idor = self.results.get('idor', {})
        if idor.get('vulnerable'):
            score += 15
        
        # المصادقة
        auth = self.results.get('authentication', {})
        if not auth.get('has_rate_limit'):
            score += 10
        if auth.get('weak_password_allowed'):
            score += 15
        if not auth.get('has_mfa'):
            score += 5
        
        # رفع الملفات
        file_upload = self.results.get('file_upload', {})
        if file_upload.get('vulnerable'):
            score += 20
        
        # CSRF
        csrf = self.results.get('csrf', {})
        if csrf.get('vulnerable'):
            score += 10
        
        return min(score, 100)
    
    def generate_recommendations(self) -> List[Dict]:
        """إنشاء توصيات بناءً على النتائج"""
        recommendations = []
        
        # رؤوس الأمان
        security_headers = self.results.get('security_headers', {})
        missing = security_headers.get('missing_critical', [])
        if 'strict-transport-security' in missing:
            recommendations.append({
                'title': 'تفعيل HSTS (Strict-Transport-Security)',
                'description': 'أضف الرأس التالي في إعدادات الخادم: Strict-Transport-Security: max-age=31536000; includeSubDomains'
            })
        if 'content-security-policy' in missing:
            recommendations.append({
                'title': 'تفعيل CSP (Content-Security-Policy)',
                'description': 'قم بتعريف سياسة أمان المحتوى لمنع هجمات XSS واختراق البيانات'
            })
        
        # SSL
        ssl = self.results.get('ssl_tls', {})
        if not ssl.get('valid'):
            recommendations.append({
                'title': 'تثبيت شهادة SSL صالحة',
                'description': 'قم بتجديد أو تثبيت شهادة SSL من جهة موثوقة مثل Let\'s Encrypt'
            })
        if ssl.get('heartbleed'):
            recommendations.append({
                'title': 'تحديث OpenSSL لإصلاح ثغرة Heartbleed',
                'description': 'قم بتحديث OpenSSL إلى الإصدار 1.0.1g أو أحدث'
            })
        
        # الملفات الحساسة
        sensitive_files = self.results.get('sensitive_files', [])
        for file in sensitive_files:
            if file.get('critical'):
                recommendations.append({
                    'title': f'إخفاء أو حماية {file["path"]}',
                    'description': f'تم اكتشاف ملف حساس في {file["path"]}. قم بإزالته أو حمايته بكلمة مرور'
                })
        
        # SQL Injection
        sql = self.results.get('sql_injection', {})
        if sql.get('vulnerable'):
            recommendations.append({
                'title': 'إصلاح ثغرات SQL Injection',
                'description': 'استخدم Prepared Statements أو ORM بدلاً من دمج المدخلات مباشرة في استعلامات SQL'
            })
        
        # XSS
        xss = self.results.get('xss', {})
        if xss.get('vulnerable'):
            recommendations.append({
                'title': 'إصلاح ثغرات XSS',
                'description': 'قم بتنقية وتشفير جميع المدخلات قبل عرضها، واستخدم CSP لمنع تنفيذ scripts غير مصرح بها'
            })
        
        # IDOR
        idor = self.results.get('idor', {})
        if idor.get('vulnerable'):
            recommendations.append({
                'title': 'إصلاح ثغرات IDOR',
                'description': 'تحقق من صلاحيات المستخدم قبل عرض أي بيانات، واستخدم معرفات عشوائية غير قابلة للتخمين'
            })
        
        # المصادقة
        auth = self.results.get('authentication', {})
        if not auth.get('has_rate_limit'):
            recommendations.append({
                'title': 'تفعيل حد لمحاولات تسجيل الدخول',
                'description': 'قم بتحديد عدد المحاولات الفاشلة (مثلاً 5 محاولات) ثم قفل الحساب مؤقتاً'
            })
        if auth.get('weak_password_allowed'):
            recommendations.append({
                'title': 'تفعيل سياسة كلمات مرور قوية',
                'description': 'تأكد من أن كلمات المرور تحتوي على 12 حرفاً على الأقل، تتضمن أحرفاً كبيرة وصغيرة وأرقاماً ورموزاً'
            })
        if not auth.get('has_mfa'):
            recommendations.append({
                'title': 'تفعيل المصادقة متعددة العوامل (MFA)',
                'description': 'أضف طبقة حماية إضافية مثل رمز OTP عبر SMS أو تطبيق Google Authenticator'
            })
        
        # المنافذ
        open_ports = self.results.get('open_ports', [])
        dangerous_ports = [3306, 5432, 6379, 27017, 9200]
        for port in open_ports:
            if port['port'] in dangerous_ports:
                recommendations.append({
                    'title': f'إغلاق المنفذ {port["port"]} ({port["service"]})',
                    'description': f'هذا المنفذ لا يجب أن يكون مفتوحاً للعامة. قم بتقييد الوصول إليه عبر جدار الحماية'
                })
        
        # رفع الملفات
        file_upload = self.results.get('file_upload', {})
        if file_upload.get('vulnerable'):
            recommendations.append({
                'title': 'تأمين رفع الملفات',
                'description': 'اقبل فقط أنواع الملفات الآمنة (صور، PDF)، وتحقق من المحتوى الفعلي، وخزن الملفات خارج المجلد العام'
            })
        
        # CSRF
        csrf = self.results.get('csrf', {})
        if csrf.get('vulnerable'):
            recommendations.append({
                'title': 'تفعيل حماية CSRF',
                'description': 'أضف tokens عشوائية لجميع النماذج وتحقق منها على الخادم، واستخدم SameSite=Strict للكوكيز'
            })
        
        # إضافة توصيات عامة إذا لم تكن هناك توصيات محددة
        if not recommendations:
            recommendations.append({
                'title': 'إجراء فحص أمني دوري',
                'description': 'يبدو أن الموقع في حالة جيدة. استمر في إجراء فحوصات دورية وتحديث الأنظمة بانتظام'
            })
        
        return recommendations
