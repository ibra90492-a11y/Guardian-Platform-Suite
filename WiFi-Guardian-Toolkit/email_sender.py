#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
أداة إرسال البريد الإلكتروني مع إرفاق الملفات
Email Sender with Attachment Support
"""

import smtplib
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

class EmailSenderApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("📧 Form to send a message - فورم إرسال رسالة")
        self.root.geometry("700x750")
        self.root.configure(bg="#0d0d0d")
        self.root.resizable(True, True)
        
        # متغير لتخزين مسار المرفق
        self.attachment_path = None
        
        self._build_ui()
        
    def _build_ui(self):
        # عنوان رئيسي
        tk.Label(self.root, text="📧 Form to send a message", 
                fg="#20ff6b", bg="#0d0d0d", font=("Tahoma", 20, "bold")).pack(pady=(15, 5))
        
        tk.Label(self.root, text="فورم إرسال رسالة - Email Sender with Attachment", 
                fg="#00d9ff", bg="#0d0d0d", font=("Tahoma", 12)).pack(pady=(0, 15))
        
        # إطار الإدخالات
        main_frame = tk.Frame(self.root, bg="#0d0d0d")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # حقل البريد الإلكتروني للمرسل
        tk.Label(main_frame, text="📧 البريد الإلكتروني للمرسل:", 
                fg="#ffffff", bg="#0d0d0d", font=("Tahoma", 11, "bold"), anchor="w").pack(fill=tk.X, pady=(0, 3))
        self.sender_entry = tk.Entry(main_frame, font=("Tahoma", 11), bg="#1a1a1a", 
                                      fg="white", insertbackground="white", relief=tk.FLAT)
        self.sender_entry.pack(fill=tk.X, pady=(0, 12), ipady=8)
        
        # حقل كلمة مرور التطبيق
        tk.Label(main_frame, text="🔑 كلمة مرور التطبيق (App Password):", 
                fg="#ffffff", bg="#0d0d0d", font=("Tahoma", 11, "bold"), anchor="w").pack(fill=tk.X, pady=(0, 3))
        self.password_entry = tk.Entry(main_frame, font=("Tahoma", 11), bg="#1a1a1a", 
                                        fg="white", insertbackground="white", relief=tk.FLAT, show="*")
        self.password_entry.pack(fill=tk.X, pady=(0, 12), ipady=8)
        
        # حقل البريد الإلكتروني للمستلم
        tk.Label(main_frame, text="📧 البريد الإلكتروني للمستلم:", 
                fg="#ffffff", bg="#0d0d0d", font=("Tahoma", 11, "bold"), anchor="w").pack(fill=tk.X, pady=(0, 3))
        self.recipient_entry = tk.Entry(main_frame, font=("Tahoma", 11), bg="#1a1a1a", 
                                         fg="white", insertbackground="white", relief=tk.FLAT)
        self.recipient_entry.pack(fill=tk.X, pady=(0, 12), ipady=8)
        
        # حقل موضوع الرسالة
        tk.Label(main_frame, text="📝 موضوع الرسالة:", 
                fg="#ffffff", bg="#0d0d0d", font=("Tahoma", 11, "bold"), anchor="w").pack(fill=tk.X, pady=(0, 3))
        self.subject_entry = tk.Entry(main_frame, font=("Tahoma", 11), bg="#1a1a1a", 
                                       fg="white", insertbackground="white", relief=tk.FLAT)
        self.subject_entry.pack(fill=tk.X, pady=(0, 12), ipady=8)
        
        # حقل نص الرسالة مع زر إدراج مرفق
        msg_frame = tk.Frame(main_frame, bg="#0d0d0d")
        msg_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        tk.Label(msg_frame, text="✏️ نص الرسالة:", 
                fg="#ffffff", bg="#0d0d0d", font=("Tahoma", 11, "bold"), anchor="w").pack(fill=tk.X, pady=(0, 3))
        
        # إطار للنص والزر
        text_frame = tk.Frame(msg_frame, bg="#0d0d0d")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.message_text = scrolledtext.ScrolledText(text_frame, height=8, bg="#1a1a1a", 
                                                        fg="#d1fae5", insertbackground="white",
                                                        font=("Tahoma", 11), wrap=tk.WORD,
                                                        relief=tk.FLAT)
        self.message_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # زر إدراج مرفق
        attach_frame = tk.Frame(text_frame, bg="#0d0d0d")
        attach_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.attach_btn = tk.Button(attach_frame, text="📎 إدراج مرفق", command=self._add_attachment,
                                     bg="#14532d", fg="white", font=("Tahoma", 11, "bold"),
                                     relief=tk.FLAT, cursor="hand2", padx=15, pady=10)
        self.attach_btn.pack(pady=5)
        
        self.attachment_label = tk.Label(attach_frame, text="لا يوجد مرفق", fg="#ff6666", 
                                          bg="#0d0d0d", font=("Tahoma", 9))
        self.attachment_label.pack(pady=5)
        
        # زر إرسال الرسالة
        send_btn = tk.Button(main_frame, text="🚀 إرسال الرسالة", command=self._send_email,
                              bg="#0f766e", fg="white", font=("Tahoma", 14, "bold"),
                              relief=tk.FLAT, cursor="hand2", padx=20, pady=12)
        send_btn.pack(pady=15)
        
        # شريط الحالة
        self.status_var = tk.StringVar(value="✅ جاهز للإرسال")
        status_bar = tk.Label(self.root, textvariable=self.status_var, fg="#20ff6b", 
                               bg="#0d0d0d", font=("Tahoma", 10), anchor="w")
        status_bar.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # إضافة نص توضيحي لكلمة مرور التطبيق
        info_frame = tk.Frame(self.root, bg="#0a0a0a", highlightthickness=1, highlightbackground="#333")
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        tk.Label(info_frame, text="ℹ️ معلومات عن كلمة مرور التطبيق:", 
                fg="#ffcc00", bg="#0a0a0a", font=("Tahoma", 10, "bold")).pack(anchor="w", padx=10, pady=(5, 0))
        tk.Label(info_frame, text="• يجب تفعيل 'التحقق بخطوتين' في حساب Gmail\n• ثم إنشاء 'كلمة مرور التطبيق' من إعدادات الأمان\n• تستخدم هذه الكلمة بدلاً من كلمة المرور العادية", 
                fg="#aaa", bg="#0a0a0a", font=("Tahoma", 9), justify="left").pack(anchor="w", padx=10, pady=(0, 5))
    
    def _add_attachment(self):
        """فتح نافذة اختيار الملف مع دعم جميع الأنواع"""
        file_types = [
            ("جميع الملفات المدعومة", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp *.ico *.pdf *.xlsx *.xls *.docx *.doc *.txt *.sh *.run *.AppImage *.deb *.rpm *.py *.pl *.apk *.apks *.xapk *.bat *.cmd *.ps1 *.vbs *.js *.html *.css *.xml *.json *.zip *.rar *.7z *.tar *.gz"),
            ("الصور", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp *.ico"),
            ("مستندات PDF", "*.pdf"),
            ("مستندات Excel", "*.xlsx *.xls"),
            ("مستندات Word", "*.docx *.doc"),
            ("ملفات نصية", "*.txt"),
            ("سكريبتات Python", "*.py"),
            ("سكريبتات Shell", "*.sh *.pl"),
            ("تطبيقات Android", "*.apk *.apks *.xapk"),
            ("حزم Linux", "*.deb *.rpm *.AppImage *.run"),
            ("ملفات Batch", "*.bat *.cmd *.ps1"),
            ("جميع الملفات", "*.*")
        ]
        
        file_path = filedialog.askopenfilename(title="اختر ملف للإرفاق", filetypes=file_types)
        
        if file_path:
            self.attachment_path = file_path
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            if file_size < 1024:
                size_str = f"{file_size} بايت"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} كيلوبايت"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} ميجابايت"
            
            self.attachment_label.config(text=f"📎 {file_name} ({size_str})", fg="#20ff6b")
            self.status_var.set(f"✅ تم إرفاق الملف: {file_name}")
    
    def _send_email(self):
        """إرسال البريد الإلكتروني مع المرفق"""
        sender = self.sender_entry.get().strip()
        password = self.password_entry.get()
        recipient = self.recipient_entry.get().strip()
        subject = self.subject_entry.get().strip()
        message = self.message_text.get("1.0", tk.END).strip()
        
        if not sender:
            self.status_var.set("❌ الرجاء إدخال البريد الإلكتروني للمرسل")
            return
        if not password:
            self.status_var.set("❌ الرجاء إدخال كلمة مرور التطبيق")
            return
        if not recipient:
            self.status_var.set("❌ الرجاء إدخال البريد الإلكتروني للمستلم")
            return
        if not subject:
            self.status_var.set("❌ الرجاء إدخال موضوع الرسالة")
            return
        if not message:
            self.status_var.set("❌ الرجاء كتابة نص الرسالة")
            return
        
        self.status_var.set("📤 جاري إرسال الرسالة...")
        self.root.update()
        
        import threading
        threading.Thread(target=self._send_email_thread, 
                        args=(sender, password, recipient, subject, message), 
                        daemon=True).start()
    
    def _send_email_thread(self, sender, password, recipient, subject, message):
        try:
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain', 'utf-8'))
            
            if self.attachment_path and os.path.exists(self.attachment_path):
                with open(self.attachment_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    
                    file_name = os.path.basename(self.attachment_path)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{file_name}"'
                    )
                    msg.attach(part)
            
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(sender, password)
            server.send_message(msg)
            server.quit()
            
            self.root.after(0, self._on_send_success)
            
        except Exception as e:
            self.root.after(0, lambda: self._on_send_error(str(e)))
    
    def _on_send_success(self):
        self.status_var.set("✅ تم إرسال الرسالة بنجاح!")
        messagebox.showinfo("نجاح", "✅ تم إرسال الرسالة بنجاح!")
    
    def _on_send_error(self, error):
        self.status_var.set(f"❌ فشل الإرسال: {error[:50]}...")
        messagebox.showerror("خطأ", f"فشل إرسال الرسالة:\n\n{error}")
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = EmailSenderApp()
    app.run()