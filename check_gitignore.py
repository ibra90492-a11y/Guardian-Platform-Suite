import os
import re

def check_gitignore():
    """التحقق من أن .env في .gitignore"""
    
    gitignore_path = ".gitignore"
    
    if not os.path.exists(gitignore_path):
        print("❌ ملف .gitignore غير موجود!")
        return False
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    patterns = [
        r'\.env',
        r'\.env\.local',
        r'secrets',
        r'credentials',
        r'token'
    ]
    
    protected_files = []
    
    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            protected_files.append(pattern)
    
    if protected_files:
        print("✅ ملف .gitignore يحمي:")
        for file in protected_files:
            print(f"   - {file}")
        return True
    else:
        print("❌ ملف .env غير محمي في .gitignore!")
        return False

def check_env_status():
    """التحقق من حالة ملف .env"""
    
    env_path = ".env"
    
    if not os.path.exists(env_path):
        print("❌ ملف .env غير موجود!")
        return False
    
    # حجم الملف
    size = os.path.getsize(env_path)
    
    # قراءة أول سطر (دون عرض التوكن)
    with open(env_path, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
    
    print(f"📄 ملف .env موجود")
    print(f"📊 الحجم: {size} بايت")
    
    # التحقق من وجود التوكن
    if "GITHUB_TOKEN=" in first_line:
        print("✅ التوكن موجود في .env")
        return True
    else:
        print("❌ التوكن غير موجود في .env")
        return False

if __name__ == "__main__":
    print("🔍 فحص أمان المشروع")
    print("=" * 50)
    
    env_status = check_env_status()
    gitignore_status = check_gitignore()
    
    print("\n" + "=" * 50)
    
    if env_status and gitignore_status:
        print("🎉 كل شيء آمن!")
        print("🔒 التوكن محمي في .env")
        print("🚫 .env في .gitignore (لن يظهر على GitHub)")
    elif not env_status:
        print("⚠️ تحتاج إلى إنشاء ملف .env")
    elif not gitignore_status:
        print("⚠️ تحتاج إلى إضافة .env إلى .gitignore")
