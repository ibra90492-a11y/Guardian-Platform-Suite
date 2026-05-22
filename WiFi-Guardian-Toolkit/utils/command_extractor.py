# -*- coding: utf-8 -*-
"""استخراج الأوامر الصالحة للتنفيذ من نصوص الردود"""

import re
from utils.constants import VALID_COMMANDS, SKIP_PATTERNS


def extract_terminal_command(text):
    """استخراج الأمر الصالح للتنفيذ من رد Codex"""
    if not text or not text.strip():
        return ""
    
    cleaned = remove_emojis(text)
    cleaned = remove_descriptive_prefixes(cleaned)
    
    # البحث عن أوامر حقيقية
    lines = cleaned.split('\n')
    command_lines = []
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        if is_skip_line(stripped):
            continue
        
        if is_valid_command(stripped):
            command_lines.append(stripped)
    
    if command_lines:
        return '\n'.join(command_lines)
    
    # محاولة استخراج كود من علامات ```
    code_match = re.search(r'```(?:\w+)?\s*(.*?)```', cleaned, re.DOTALL)
    if code_match:
        code_content = remove_emojis(code_match.group(1))
        return code_content.strip()
    
    return ""


def remove_emojis(text):
    """إزالة جميع الإيموجي والرموز التعبيرية"""
    # إزالة الإيموجي
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002700-\U000027BF"  # dingbats
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    text = emoji_pattern.sub('', text)
    
    # إزالة الرموز الخاصة
    special_symbols = r'[✅⚡⚠️📦📁❌📤📋🔄🗑️💻📝🎯🚀📊🔧🛡️🌐⚙️📧💻🖥️🔒🔐📍🏢🏛️📄]'
    text = re.sub(special_symbols, '', text)
    
    # إزالة الرموز الترميزية
    text = re.sub(r'[░▒▓█▀▄■□▲▼▶◀↓↑→←]', '', text)
    
    return text


def remove_descriptive_prefixes(text):
    """إزالة البادئات الوصفية مثل 'تم إنشاء' وما شابه"""
    # إزالة الأسطر التي تبدأ برموز
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # إزالة البادئات
        line = re.sub(r'^[📦📁✅⚡⚠️❌📤📋🔄🗑️💻📝🎯🚀📊]*\s*', '', line)
        line = re.sub(r'^(تم إنشاء|تم حفظ|تم نسخ|تم لصق|فشل|خطأ|تم إرسال|جاري)\s*', '', line)
        if line.strip():
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def is_skip_line(line):
    """تحديد ما إذا كان السطر يجب تخطيه"""
    line_lower = line.lower()
    for pattern in SKIP_PATTERNS:
        if pattern.lower() in line_lower:
            return True
    return False


def is_valid_command(line):
    """تحديد ما إذا كان السطر أمراً صالحاً للتنفيذ"""
    if not line.strip():
        return False
    
    # تقسيم السطر إلى كلمات
    parts = line.strip().split()
    if not parts:
        return False
    
    first_word = parts[0].lower()
    
    # أوامر Windows (ipconfig, netsh, etc.)
    if first_word in VALID_COMMANDS:
        return True
    
    # أوامر PowerShell
    if first_word.startswith(('get-', 'set-', 'test-', 'invoke-')):
        return True
    
    # أوامر sudo
    if first_word == 'sudo' and len(parts) > 1 and parts[1].lower() in VALID_COMMANDS:
        return True
    
    # أوامر wsl
    if first_word == 'wsl' and len(parts) > 1:
        return True
    
    # مسارات أوامر Windows (C:\...)
    if re.match(r'^[A-Za-z]:\\.+\.exe', first_word, re.IGNORECASE):
        return True
    
    return False


def is_python_script(text):
    """تحديد ما إذا كان النص سكربت Python كامل"""
    if not text:
        return False
    
    indicators = [
        '#!/usr/bin/env python3',
        '# -*- coding:',
        'import sys',
        'if __name__ == "__main__"',
        'def ',
        'class '
    ]
    
    for indicator in indicators:
        if indicator in text:
            return True
    
    return False
