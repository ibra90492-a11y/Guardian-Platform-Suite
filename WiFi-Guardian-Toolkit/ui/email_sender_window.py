"""EmailSenderWindow UI mixin."""

import os
import subprocess
import sys
from tkinter import messagebox


class EmailSenderWindowMixin:
    def open_email_sender(self):
        """فتح نافذة إرسال البريد الإلكتروني (Form to send a message)"""
        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            script_path = os.path.join(script_dir, "email_sender.py")

            if os.path.exists(script_path):
                subprocess.Popen([sys.executable, script_path])
            else:
                messagebox.showerror("خطأ", f"الملف email_sender.py غير موجود في مجلد المشروع!\n\nالرجاء وضعه في:\n{script_path}")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل فتح نافذة إرسال البريد:\n{e}")

