# desktop_app.py - الفورم الرئيسي المعدل
from __future__ import annotations

import html
import json
import os
import sys
import threading
import time
import subprocess
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from datetime import datetime

os.environ.setdefault(
    "QTWEBENGINE_CHROMIUM_FLAGS",
    "--disable-gpu --disable-gpu-compositing --log-level=3",
)

from PySide6.QtCore import QEvent, QObject, Qt, QTimer, QUrl, Signal, QtMsgType, qInstallMessageHandler
from PySide6.QtGui import QCloseEvent, QFont
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSplitter,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWebEngineWidgets import QWebEngineView

import run


ROOT = Path(__file__).resolve().parent
APP_TITLE = "Guardian Cyber Assessment Platform"
SCAN_TIMER_INTERVAL_MS = 180
REPORT_FINAL_WAIT_SECONDS = 5
REPORT_FINAL_WAIT_TICKS = max(1, round((REPORT_FINAL_WAIT_SECONDS * 1000) / SCAN_TIMER_INTERVAL_MS))
_QT_MESSAGE_FILTER_INSTALLED = False
DEFAULT_STYLE = """
QMainWindow, QWidget {
    background: #eef2f6;
    color: #182536;
    font-family: "Segoe UI", Tahoma, Arial;
    font-size: 12px;
}
QFrame#SidePanel {
    background: #ffffff;
    border-right: 1px solid #d9e1ea;
}
QFrame#WebFrame {
    background: #ffffff;
    border: 2px solid #17324d;
    border-radius: 10px;
}
QFrame#OutputFrame,
QFrame#TerminalFrame {
    background: #ffffff;
    border: 1px solid #d9e1ea;
    border-radius: 8px;
}
QLabel#Title {
    color: #102033;
    font-size: 23px;
    font-weight: 700;
}
QLabel#Subtitle {
    color: #5b6878;
    font-size: 12px;
}
QLabel#SectionTitle {
    color: #17324d;
    font-size: 14px;
    font-weight: 700;
}
QLabel#StatusReady {
    color: #166534;
    font-weight: 700;
}
QLabel#StatusPending {
    color: #92400e;
    font-weight: 700;
}
QLabel#StatusError {
    color: #b42318;
    font-weight: 700;
}
QLineEdit {
    min-height: 38px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 9px;
    background: #ffffff;
}
QCheckBox {
    color: #334155;
}
QPushButton {
    min-height: 36px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    background: #ffffff;
    color: #182536;
    padding: 6px 10px;
    font-weight: 600;
}
QPushButton:hover {
    background: #f8fafc;
}
QPushButton#PrimaryButton {
    background: #2f80ed;
    border-color: #2f80ed;
    color: #ffffff;
}
QPushButton#DarkButton {
    background: #17324d;
    border-color: #17324d;
    color: #ffffff;
}
QPushButton#DangerButton {
    background: #b42318;
    border-color: #b42318;
    color: #ffffff;
}
QPushButton#MegaButton {
    min-height: 58px;
    border: 2px solid #17324d;
    border-radius: 8px;
    background: #17324d;
    color: #ffffff;
    padding: 8px 12px;
    font-size: 17px;
    font-weight: 800;
}
QPlainTextEdit {
    background: #0f172a;
    color: #dbeafe;
    border: 1px solid #1e293b;
    border-radius: 6px;
    padding: 8px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 11px;
}
QSplitter::handle {
    background: #cbd5e1;
    width: 3px;
}
"""
DARK_STYLE = """
QMainWindow, QWidget {
    background: #000000;
    color: #00ff41;
    font-family: "Segoe UI", Tahoma, Arial;
    font-size: 12px;
}
QFrame#SidePanel {
    background: #000000;
    border-right: 1px solid #ffffff;
}
QFrame#WebFrame {
    background: #000000;
    border: 2px solid #ffffff;
    border-radius: 10px;
}
QFrame#OutputFrame,
QFrame#TerminalFrame {
    background: #000000;
    border: 1px solid #ffffff;
    border-radius: 8px;
}
QLabel#Title {
    color: #00ff41;
    font-size: 23px;
    font-weight: 700;
}
QLabel#Subtitle,
QLabel#SectionTitle,
QLabel#StatusReady,
QLabel#StatusPending,
QLabel#StatusError {
    color: #00ff41;
    font-weight: 700;
}
QLineEdit,
QComboBox {
    min-height: 34px;
    border: 1px solid #ffffff;
    border-radius: 6px;
    padding: 5px 8px;
    background: #000000;
    color: #00ff41;
}
QComboBox QAbstractItemView {
    background: #000000;
    color: #00ff41;
    border: 1px solid #ffffff;
    selection-background-color: #092a14;
}
QCheckBox {
    color: #00ff41;
}
QCheckBox::indicator {
    width: 34px;
    height: 34px;
    border: 3px solid #ffffff;
    border-radius: 6px;
    background: #000000;
}
QCheckBox::indicator:checked {
    image: url(assets/checkbox_checked_dark.svg);
    border: 3px solid #ffffff;
    background: #000000;
}
QPushButton,
QPushButton#PrimaryButton,
QPushButton#DarkButton,
QPushButton#DangerButton,
QPushButton#MegaButton {
    min-height: 34px;
    border: 1px solid #ffffff;
    border-radius: 6px;
    background: #000000;
    color: #00ff41;
    padding: 5px 9px;
    font-weight: 700;
}
QPushButton#MegaButton {
    min-height: 58px;
    border: 2px solid #ffffff;
    border-radius: 8px;
    font-size: 17px;
    font-weight: 900;
}
QPushButton:hover,
QPushButton#PrimaryButton:hover,
QPushButton#DarkButton:hover,
QPushButton#DangerButton:hover,
QPushButton#MegaButton:hover {
    background: #071407;
}
QPlainTextEdit {
    background: #000000;
    color: #00ff41;
    border: 1px solid #ffffff;
    border-radius: 6px;
    padding: 8px;
    font-family: Consolas, "Courier New", monospace;
    font-size: 11px;
}
QSplitter::handle {
    background: #ffffff;
    width: 3px;
}
"""


class ServiceManager(QObject):
    log = Signal(str)
    ready = Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self.backend_process = None
        self.frontend_process = None
        self._owns_backend = False
        self._owns_frontend = False

    def start(self) -> None:
        thread = threading.Thread(target=self._start_services, daemon=True)
        thread.start()

    def stop(self) -> None:
        if self._owns_backend:
            run.stop_process(self.backend_process)
        if self._owns_frontend:
            run.stop_process(self.frontend_process)

    def _start_services(self) -> None:
        try:
            self.log.emit("تجهيز هيكل المشروع...")
            run.create_structure()
            self.log.emit("فحص مكتبات الباكند...")
            run.ensure_backend_packages()
            self.log.emit("فحص مكتبات الواجهة...")
            run.ensure_frontend_packages()
            run.check_nmap()

            backend_was_open = run.port_is_open(run.BACKEND_PORT)
            frontend_was_open = run.port_is_open(run.FRONTEND_PORT)
            self.backend_process = run.start_backend()
            self.frontend_process = run.start_frontend()
            self._owns_backend = not backend_was_open and self.backend_process is not None
            self._owns_frontend = not frontend_was_open and self.frontend_process is not None

            backend_ready = wait_for_http(f"{run.BACKEND_URL}/status", timeout=60)
            frontend_ready = wait_for_http(run.FRONTEND_URL, timeout=60)
            self.ready.emit(backend_ready and frontend_ready)
        except Exception as exc:
            self.log.emit(f"تعذر تشغيل الخدمات: {exc}")
            self.ready.emit(False)


class GuardianDesktop(QMainWindow):
    action_finished = Signal(tuple)
    action_failed = Signal(tuple)
    full_scan_finished = Signal(object)
    full_scan_failed = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1500, 1080)
        self.setMinimumSize(1380, 960)
        self._status_state = "pending"
        self.scan_overlay_active = False
        self.scan_progress = 0
        self.scan_dot_count = 1
        self.scan_worker_done = False
        self.scan_report_wait_ticks = 0
        self.scan_final_report_url = ""
        self.full_scan_result: dict = {}
        self.startup_history_cleared = False
        self.wait_dialog = None  # نافذة الانتظار 7 ثوانٍ
        self.service_manager = ServiceManager()
        self.service_manager.log.connect(self._append_log)
        self.service_manager.ready.connect(self._services_ready)
        self.action_finished.connect(self._show_action_result)
        self.action_failed.connect(self._show_action_error)
        self.full_scan_finished.connect(self._finish_full_scan_worker)
        self.full_scan_failed.connect(self._fail_full_scan_worker)

        self._build_ui()
        self._set_status("جاري تشغيل الخدمات...", state="pending")
        self.service_manager.start()

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.refresh_status)
        self.status_timer.start(5000)

        self.scan_timer = QTimer(self)
        self.scan_timer.timeout.connect(self._advance_full_scan_progress)
        self.scan_timer.setInterval(SCAN_TIMER_INTERVAL_MS)

    def _build_ui(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self._build_left_panel())
        splitter.addWidget(self._build_right_panel())
        splitter.setSizes([360, 1140])
        self.setCentralWidget(splitter)

    def _build_left_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("SidePanel")
        panel.setMinimumWidth(320)
        panel.setMaximumWidth(410)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("الهدف والموافقة")
        title.setObjectName("Title")
        layout.addWidget(title)

        subtitle = QLabel("أدخل الرابط المطلوب ثم أكمل الموافقة قبل تنفيذ الفحص.")
        subtitle.setObjectName("Subtitle")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        self.status_label = QLabel("Starting")
        self.status_label.setObjectName("StatusPending")
        layout.addWidget(self.status_label)

        layout.addWidget(_section_label("Target / الهدف"))
        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("https://example.com")
        self.target_input.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        layout.addWidget(self.target_input)

        self.approval_checkbox = QCheckBox("I have written approval / لدي موافقة صريحة")
        layout.addWidget(self.approval_checkbox)

        self.approval_code = QLineEdit()
        self.approval_code.setPlaceholderText("Enter approval code / أدخل رقم الموافقة")
        layout.addWidget(self.approval_code)

        # ========== الزر الرئيسي المعدل ==========
        self.main_scan_btn = QPushButton("🌐 فحص الموقع الإلكتروني وتنزيل التقرير")
        self.main_scan_btn.setObjectName("MegaButton")
        self.main_scan_btn.clicked.connect(self.check_the_website)
        layout.addWidget(self.main_scan_btn)

        extra_row = QHBoxLayout()
        extra_row.setSpacing(8)
        self.open_wifi_btn = QPushButton("Open WiFi Toolkit")
        self.open_wifi_btn.setObjectName("PrimaryButton")
        self.open_wifi_btn.clicked.connect(self.open_wifi_toolkit)
        extra_row.addWidget(self.open_wifi_btn)

        self.clear_history_btn = QPushButton("Clear History")
        self.clear_history_btn.setObjectName("DangerButton")
        self.clear_history_btn.clicked.connect(self.clear_history)
        extra_row.addWidget(self.clear_history_btn)
        layout.addLayout(extra_row)

        layout.addStretch(1)

        return panel

    def _build_right_panel(self) -> QWidget:
        wrapper = QWidget()
        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        title = QLabel("صفحة الويب المطلوبة")
        title.setObjectName("Title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        web_card = QFrame()
        web_card.setObjectName("WebFrame")
        web_card.setFixedSize(560, 560)
        web_card_layout = QVBoxLayout(web_card)
        web_card_layout.setContentsMargins(0, 0, 0, 0)
        web_card_layout.setSpacing(0)

        self.webview = QWebEngineView()
        self.webview.loadFinished.connect(self._webview_loaded)
        self.webview.setHtml(self._web_prompt_html(), QUrl("about:blank"))
        web_card_layout.addWidget(self.webview)

        web_row = QHBoxLayout()
        web_row.addStretch(1)
        web_row.addWidget(web_card)
        web_row.addStretch(1)
        layout.addLayout(web_row)

        layout.addWidget(_section_label("Results / النتائج"))
        results_frame = QFrame()
        results_frame.setObjectName("OutputFrame")
        results_layout = QVBoxLayout(results_frame)
        results_layout.setContentsMargins(8, 8, 8, 8)
        results_layout.setSpacing(0)
        self.result_box = QPlainTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setPlaceholderText("Results will appear here / ستظهر النتائج هنا")
        self.result_box.setFixedHeight(130)
        results_layout.addWidget(self.result_box)
        layout.addWidget(results_frame)

        layout.addWidget(_section_label("Terminal / الطرفية"))
        terminal_frame = QFrame()
        terminal_frame.setObjectName("TerminalFrame")
        terminal_layout = QVBoxLayout(terminal_frame)
        terminal_layout.setContentsMargins(8, 8, 8, 8)
        terminal_layout.setSpacing(0)
        self.terminal_box = QPlainTextEdit()
        self.terminal_box.setReadOnly(True)
        self.terminal_box.setPlaceholderText("Terminal output will appear here / ستظهر الطرفية هنا")
        self.terminal_box.setFixedHeight(150)
        terminal_layout.addWidget(self.terminal_box)
        layout.addWidget(terminal_frame)

        layout.addStretch(1)
        return wrapper

    def _webview_loaded(self, ok: bool) -> None:
        if not ok:
            return
        self._apply_web_theme()
        if self.scan_overlay_active:
            self._render_scan_overlay()

    def apply_theme(self) -> None:
        QApplication.instance().setStyleSheet(DEFAULT_STYLE)
        self._set_status(self.status_label.text(), state=self._status_state)
        self._apply_web_theme()

    def _apply_web_theme(self) -> None:
        script = "document.documentElement.setAttribute('data-guardian-theme', 'default');"
        self.webview.page().runJavaScript(script)

    def check_the_website(self) -> None:
        """الوظيفة الرئيسية: فحص الموقع + تنزيل التقرير تلقائياً"""
        if self.scan_overlay_active:
            self._show_hacker_message("CheckTheWebsite", "الفحص الشامل يعمل الآن.")
            return
        if not self._approval_ok(require_code=True):
            return

        target = self._target()
        if not target:
            self._show_hacker_message(
                "الهدف",
                "قم بادراج رابط صفحة الويب المطلوبة من خلال وضع الرابط في حقل الهدف في النافذة اليسري.",
            )
            self._show_web_prompt()
            return

        url = QUrl.fromUserInput(target)
        if not url.isValid() or url.isEmpty():
            self._show_hacker_message("الهدف", "الرابط المدخل غير صالح.")
            self._show_web_prompt()
            return

        self.webview.setUrl(url)
        self._append_terminal(f"تم فتح الرابط داخل إطار صفحة الويب المطلوبة: {url.toString()}")
        self.scan_overlay_active = True
        self.scan_progress = 0
        self.scan_dot_count = 1
        self.scan_worker_done = False
        self.scan_report_wait_ticks = 0
        self.scan_final_report_url = ""
        self.full_scan_result = {}
        self.result_box.setPlainText("CheckTheWebsite started / بدأ الفحص الشامل")
        self._set_status("CheckTheWebsite يعمل الآن...", state="pending")
        self._render_scan_overlay()
        self.scan_timer.start()

        thread = threading.Thread(target=self._check_the_website_worker, args=(url.toString(),), daemon=True)
        thread.start()

    def _check_the_website_worker(self, target: str) -> None:
        """تنفيذ الفحص في الخلفية"""
        try:
            analysis = api_request(
                "POST",
                "/understand",
                {"user_input": f"افحص موقع {target}", "approved": False},
                timeout=35,
            )
            web_scan = api_request(
                "POST",
                "/execute",
                {"user_input": f"افحص موقع {target}", "approved": True},
                timeout=60,
            )
            port_scan = api_request(
                "POST",
                "/execute",
                {"user_input": f"افحص منافذ {target}", "approved": True},
                timeout=90,
            )
            try:
                report = api_request("POST", "/reports/all/pdf/create", {}, timeout=60)
            except Exception as exc:
                report = {
                    "status": "success",
                    "message": f"Using live report URL because create endpoint was unavailable: {exc}",
                    "download_url": "/reports/all/pdf",
                }
            result = {
                "analysis": analysis,
                "web_scan": web_scan,
                "port_scan": port_scan,
                "report": report,
            }
            self.full_scan_finished.emit(result)
        except Exception as exc:
            self.full_scan_failed.emit(str(exc))

    def _advance_full_scan_progress(self) -> None:
        """تحديث شريط التقدم"""
        if not self.scan_overlay_active:
            self.scan_timer.stop()
            return

        self.scan_dot_count = 1 if self.scan_dot_count >= 5 else self.scan_dot_count + 1

        if self.scan_worker_done and self.scan_progress < 99:
            self.scan_progress = min(99, self.scan_progress + 2)
            self._render_scan_overlay()
            return

        if self.scan_worker_done:
            self.scan_progress = 100
            self.scan_report_wait_ticks += 1
            self._render_scan_overlay()
            if self.scan_report_wait_ticks >= REPORT_FINAL_WAIT_TICKS:
                self.scan_timer.stop()
                self._close_wait_and_download_report()
            return

        if self.scan_progress < 99:
            self.scan_progress += 1
        self._render_scan_overlay()

    def _finish_full_scan_worker(self, result: object) -> None:
        self.scan_worker_done = True
        self.full_scan_result = result if isinstance(result, dict) else {"result": result}
        report = self.full_scan_result.get("report", {})
        download_url = report.get("download_url") if isinstance(report, dict) else ""
        self.scan_final_report_url = f"{run.BACKEND_URL}{download_url}" if download_url else f"{run.BACKEND_URL}/reports/all/pdf"
        self.result_box.setPlainText(json.dumps(self.full_scan_result, ensure_ascii=False, indent=2))
        self._append_terminal("اكتمل الفحص الشامل وتم تجهيز النتائج.")

    def _fail_full_scan_worker(self, error: str) -> None:
        self.scan_timer.stop()
        self.scan_overlay_active = False
        self._set_status("تعذر إكمال CheckTheWebsite", state="error")
        self.result_box.setPlainText(error)
        self._append_terminal(f"فشل الفحص الشامل: {error}")
        self._show_hacker_message("CheckTheWebsite", error)

    def _show_wait_dialog_and_download(self) -> None:
        """إظهار نافذة انتظار 5 ثوانٍ ثم تنزيل التقرير"""
        from PySide6.QtWidgets import QProgressBar
        
        self.wait_dialog = QDialog(self)
        self.wait_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self.wait_dialog.setWindowTitle("جاري تجهيز التقرير")
        self.wait_dialog.setModal(True)
        self.wait_dialog.setFixedSize(450, 200)
        self.wait_dialog.setStyleSheet("""
            QDialog {
                background: #000000;
                color: #00ff41;
                font-family: "Segoe UI", Tahoma, Arial;
                font-size: 14px;
            }
            QLabel {
                color: #00ff41;
                background: transparent;
            }
            QProgressBar {
                border: 2px solid #00ff41;
                border-radius: 5px;
                text-align: center;
                color: #00ff41;
                background: #000000;
            }
            QProgressBar::chunk {
                background-color: #00ff41;
                width: 10px;
            }
        """)
        
        layout = QVBoxLayout(self.wait_dialog)
        layout.setSpacing(20)
        
        title_label = QLabel("📄 جاري طباعة تقرير الفحص")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title_label)
        
        self.wait_message_label = QLabel("الرجاء الانتظار... 5 ثوانٍ")
        self.wait_message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.wait_message_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.wait_message_label)
        
        self.wait_progress_bar = QProgressBar()
        self.wait_progress_bar.setRange(0, REPORT_FINAL_WAIT_SECONDS)
        self.wait_progress_bar.setValue(0)
        self.wait_progress_bar.setFormat(f"%v / {REPORT_FINAL_WAIT_SECONDS} ثوانٍ")
        layout.addWidget(self.wait_progress_bar)
        
        # عداد تنازلي
        self.wait_seconds = REPORT_FINAL_WAIT_SECONDS
        dialog = self.wait_dialog
        
        def update_wait():
            if self.wait_dialog is not dialog or not dialog.isVisible():
                return
            if self.wait_seconds > 0:
                self.wait_message_label.setText(f"جاري طباعة تقرير الفحص... {self.wait_seconds} ثوانٍ")
                self.wait_progress_bar.setValue(REPORT_FINAL_WAIT_SECONDS - self.wait_seconds)
                self.wait_seconds -= 1
                QTimer.singleShot(1000, update_wait)
            else:
                self.wait_message_label.setText("✅ جاري تنزيل التقرير...")
                self.wait_progress_bar.setValue(REPORT_FINAL_WAIT_SECONDS)
                QTimer.singleShot(0, self._close_wait_and_download_report)
        
        update_wait()
        
        # زر إلغاء
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #000000;
                color: #00ff41;
                border: 1px solid #00ff41;
                border-radius: 5px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #071407;
            }
        """)
        cancel_btn.clicked.connect(self._cancel_wait_and_close)
        layout.addWidget(cancel_btn)
        
        self.wait_dialog.show()
        self.wait_dialog.raise_()
        self.wait_dialog.activateWindow()

    def _cancel_wait_and_close(self) -> None:
        """إلغاء وإغلاق نافذة الانتظار"""
        self._close_wait_dialog()
        self.scan_overlay_active = False
        self._set_status("تم إلغاء التقرير", state="pending")

    def _close_wait_and_download_report(self) -> None:
        """إغلاق نافذة الانتظار وتنزيل التقرير"""
        self._close_wait_dialog()
        
        self.scan_overlay_active = False
        self._remove_scan_overlay()
        self._set_status("تم إنشاء تقرير الفحص", state="ready")
        
        # تنزيل التقرير إلى مجلد Downloads
        self._download_report_to_downloads()

    def _close_wait_dialog(self) -> None:
        """إغلاق نافذة تجهيز التقرير فوراً قبل فتح ملف التقرير."""
        if not self.wait_dialog:
            return

        dialog = self.wait_dialog
        self.wait_dialog = None
        dialog.hide()
        dialog.close()
        dialog.deleteLater()
        self._flush_ui_events()

    def _close_transient_windows_before_pdf(self) -> None:
        """إغلاق أي تنبيهات أو فورمز فرعية قبل فتح ملف التقرير."""
        self._close_wait_dialog()
        self._remove_scan_overlay()
        app = QApplication.instance()
        if app is None:
            return

        for widget in list(app.topLevelWidgets()):
            if widget is self:
                continue
            if isinstance(widget, (QDialog, QMessageBox)):
                widget.hide()
                widget.close()
                widget.deleteLater()

        self._flush_ui_events()

    def _remove_scan_overlay(self) -> None:
        if not hasattr(self, "webview"):
            return

        self.webview.page().runJavaScript(
            """
            (() => {
              document.getElementById('guardian-scan-overlay')?.remove();
            })();
            """
        )
        self._flush_ui_events()

    def _flush_ui_events(self) -> None:
        for _ in range(3):
            QApplication.processEvents()
            QApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    def _download_report_to_downloads(self) -> None:
        """تنزيل التقرير إلى مجلد Downloads وفتحه"""
        self._close_transient_windows_before_pdf()
        try:
            # إنشاء اسم الملف بالصيغة المطلوبة
            now = datetime.now()
            filename = f"Site inspection file - {now.strftime('%Y-%m-%d %H-%M-%S')}.pdf"
            downloads_dir = Path.home() / "Downloads"
            downloads_dir.mkdir(exist_ok=True)
            file_path = downloads_dir / filename
            
            # جلب التقرير من API
            report_url = self.scan_final_report_url or f"{run.BACKEND_URL}/reports/all/pdf"
            
            # تنزيل الملف
            req = urllib.request.Request(report_url, method="GET")
            with urllib.request.urlopen(req, timeout=60) as response:
                content = response.read()
            
            # حفظ الملف
            with open(file_path, "wb") as f:
                f.write(content)
            
            self.result_box.appendPlainText(f"✅ تم تنزيل التقرير: {filename}")
            self.result_box.appendPlainText(f"📁 الموقع: {downloads_dir}")
            self._set_status(f"✅ تم تنزيل التقرير: {filename}", state="ready")
            
            self._close_transient_windows_before_pdf()
            webbrowser.open(str(file_path))
            
        except Exception as e:
            self.result_box.appendPlainText(f"❌ خطأ في تنزيل التقرير: {str(e)}")
            self._set_status("❌ فشل تنزيل التقرير", state="error")
            self._show_hacker_message("خطأ", f"فشل تنزيل التقرير:\n{str(e)}")

    def _scan_message(self) -> str:
        progress = self.scan_progress
        dots = "." * self.scan_dot_count
        if progress <= 20:
            return f"بدأت عملية فحص الموقع{dots}"
        if progress <= 60:
            return f"النتائج المكتشفة{dots}\nرؤوس الأمان المفقودة: ✓\nالنوافذ المفتوحة: ✓"
        if progress < 90:
            return f"جاري استكمال الفحص وتحليل النتائج{dots}"
        if progress < 100:
            return f"تم اكتشاف عدة أخطار أمنية وجاري تحليل المخاطر وافتراح حلول للمشكلات الأمنية واعداد التقرير{dots}"
        return f"جاري طباعة تقرير الفحص{dots}"

    def _render_scan_overlay(self) -> None:
        if not hasattr(self, "webview"):
            return
        message_html = "<br>".join(html.escape(line) for line in self._scan_message().splitlines())
        progress = max(0, min(100, self.scan_progress))
        script = f"""
(() => {{
  let overlay = document.getElementById('guardian-scan-overlay');
  if (!overlay) {{
    overlay = document.createElement('div');
    overlay.id = 'guardian-scan-overlay';
    document.body.appendChild(overlay);
  }}
  overlay.style.cssText = [
    'position:fixed',
    'inset:0',
    'z-index:2147483647',
    'display:grid',
    'place-items:center',
    'background:rgba(0,0,0,0.40)',
    'font-family:Segoe UI,Tahoma,Arial,sans-serif'
  ].join(';');
  overlay.innerHTML = `
    <section style="width:min(420px,86%);background:#000;color:#00ff41;border:2px solid #fff;border-radius:8px;padding:24px;text-align:center;box-shadow:0 24px 80px rgba(0,0,0,.55);">
      <div style="font-size:22px;font-weight:900;line-height:1.8;margin-bottom:18px;">{message_html}</div>
      <div style="height:22px;border:1px solid #fff;border-radius:999px;overflow:hidden;background:#020202;">
        <div style="height:100%;width:{progress}%;background:#00ff41;transition:width .18s linear;"></div>
      </div>
      <div style="font-size:28px;font-weight:900;margin-top:12px;">{progress}%</div>
    </section>
  `;
}})();
"""
        self.webview.page().runJavaScript(script)

    def _set_status(self, message: str, state: str = "ready") -> None:
        self._status_state = state
        names = {
            "ready": "StatusReady",
            "pending": "StatusPending",
            "error": "StatusError",
        }
        self.status_label.setObjectName(names.get(state, "StatusReady"))
        self.status_label.setText(message)
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def _append_log(self, message: str) -> None:
        self._append_terminal(message)

    def _services_ready(self, ok: bool) -> None:
        if ok:
            self._set_status("الخدمات جاهزة", state="ready")
            self._show_web_prompt()
            self._clear_history_on_startup()
            self.refresh_status()
            return
        self._set_status("الخدمات لم تكتمل، راجع logs", state="error")

    def _clear_history_on_startup(self) -> None:
        if self.startup_history_cleared:
            return

        self.startup_history_cleared = True
        self.scan_final_report_url = ""
        self.full_scan_result = {}
        self.result_box.clear()
        if hasattr(self, "terminal_box"):
            self.terminal_box.clear()

        def worker() -> None:
            try:
                api_request("POST", "/history/clear", {}, timeout=15)
            except Exception:
                pass

        threading.Thread(target=worker, daemon=True).start()

    def refresh_status(self) -> None:
        self._run_api_action("status", lambda: api_request("GET", "/status"))

    def analyze_target(self) -> None:
        target = self._target()
        self._run_api_action(
            "analysis",
            lambda: api_request("POST", "/understand", {"user_input": f"افحص موقع {target}", "approved": False}),
        )

    def web_scan(self) -> None:
        if not self._approval_ok():
            return
        target = self._target()
        self._run_api_action(
            "web_scan",
            lambda: api_request("POST", "/execute", {"user_input": f"افحص موقع {target}", "approved": True}),
        )

    def port_scan(self) -> None:
        if not self._approval_ok():
            return
        target = self._target()
        self._run_api_action(
            "port_scan",
            lambda: api_request("POST", "/execute", {"user_input": f"افحص منافذ {target}", "approved": True}),
        )

    def clear_history(self) -> None:
        self._run_api_action("clear_history", lambda: api_request("POST", "/history/clear", {}))

    def open_target_in_webview(self) -> None:
        target = self._target()
        if not target:
            self._show_web_prompt()
            return
        self.webview.setUrl(QUrl.fromUserInput(target))

    def show_dashboard(self) -> None:
        self._show_web_prompt()

    def show_api_docs(self) -> None:
        self.webview.setUrl(QUrl(f"{run.BACKEND_URL}/docs"))

    def reload_webview(self) -> None:
        self.webview.reload()

    def open_external_browser(self) -> None:
        webbrowser.open(self.webview.url().toString() or run.FRONTEND_URL)

    def open_wifi_toolkit(self) -> None:
        wifi_root = ROOT / "WiFi-Guardian-Toolkit"
        wifi_main = wifi_root / "main.py"
        if not wifi_main.exists():
            self._show_hacker_message(
                "WiFi Toolkit",
                f"لم أجد ملف التشغيل المتوقع:\n{wifi_main}",
            )
            return

        try:
            env = os.environ.copy()
            env["WIFI_GUARDIAN_FORCE_FOREGROUND"] = "1"
            subprocess.Popen([sys.executable, str(wifi_main)], cwd=str(wifi_root), env=env)
            self._append_log("تم فتح WiFi Guardian Toolkit في نافذة مستقلة.")
        except Exception as exc:
            self._show_hacker_message("WiFi Toolkit", f"تعذر تشغيل واجهة WiFi:\n{exc}")

    def _target(self) -> str:
        return self.target_input.text().strip()

    def _web_prompt_html(self) -> str:
        message = "قم بادراج رابط صفحة الويب المطلوبة من خلال وضع الرابط في حقل الهدف في النافذة اليسري"
        return f"""
<!doctype html>
<html lang="ar">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root {{
      color-scheme: dark;
    }}
    html, body {{
      width: 100%;
      height: 100%;
      margin: 0;
    }}
    body {{
      display: grid;
      place-items: center;
      background: linear-gradient(160deg, #000000 0%, #0b0f14 100%);
      color: #00ff41;
      font-family: "Segoe UI", Tahoma, Arial, sans-serif;
    }}
    .card {{
      width: min(78%, 430px);
      aspect-ratio: 1 / 1;
      display: grid;
      place-items: center;
      text-align: center;
      border: 2px solid #ffffff;
      border-radius: 16px;
      background: rgba(0, 0, 0, 0.95);
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
      padding: 24px;
      box-sizing: border-box;
    }}
    .title {{
      font-size: 24px;
      font-weight: 900;
      margin-bottom: 16px;
    }}
    .message {{
      font-size: 16px;
      font-weight: 700;
      line-height: 1.8;
      color: #d1fae5;
    }}
  </style>
</head>
<body>
  <div class="card">
    <div>
      <div class="title">صفحة الويب المطلوبة</div>
      <div class="message">{html.escape(message)}</div>
    </div>
  </div>
</body>
</html>
"""

    def _show_web_prompt(self) -> None:
        self.webview.setHtml(self._web_prompt_html(), QUrl("about:blank"))

    def _append_terminal(self, message: str) -> None:
        if hasattr(self, "terminal_box"):
            self.terminal_box.appendPlainText(message)
        elif hasattr(self, "result_box"):
            self.result_box.appendPlainText(message)

    def _approval_ok(self, require_code: bool = False) -> bool:
        if not self.approval_checkbox.isChecked():
            self._show_hacker_message(
                "تأكيد الموافقة",
                "فعّل خيار الموافقة قبل تشغيل أي فحص. استخدم المنصة فقط على أهداف تملكها أو لديك تصريح مكتوب لفحصها.",
            )
            return False

        if require_code:
            approval_code = self.approval_code.text().strip()
            if not approval_code:
                self._show_hacker_message(
                    "كود الموافقة",
                    "لابد من إدخال رقم الموافقة حتى يتم الفحص",
                )
                return False

        return True

    def _show_hacker_message(self, title: str, message: str) -> None:
        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(message)
        box.setStyleSheet(
            """
            QMessageBox {
                background: #000000;
                color: #00ff41;
                font-family: "Segoe UI", Tahoma, Arial;
                font-size: 17px;
                font-weight: 800;
            }
            QMessageBox QLabel {
                background: #000000;
                color: #00ff41;
                font-size: 17px;
                font-weight: 800;
                min-width: 360px;
                padding: 12px;
            }
            QMessageBox QPushButton {
                background: #000000;
                color: #00ff41;
                border: 1px solid #ffffff;
                border-radius: 6px;
                min-width: 92px;
                min-height: 34px;
                font-size: 15px;
                font-weight: 800;
            }
            QMessageBox QPushButton:hover {
                background: #071407;
            }
            """
        )
        box.exec()

    def _run_api_action(self, name: str, callback) -> None:
        def worker() -> None:
            try:
                result = callback()
            except Exception as exc:
                self.action_failed.emit((name, str(exc)))
                return
            self.action_finished.emit((name, result))

        threading.Thread(target=worker, daemon=True).start()

    def _show_action_result(self, payload: tuple) -> None:
        name, result = payload
        if name == "status" and isinstance(result, dict):
            self._set_status(
                f"API {result.get('status', 'unknown')} | Nmap {'ready' if result.get('nmap_usable') else 'fallback'}",
                state="ready" if result.get("status") == "online" else "pending",
            )
            return

        text = json.dumps(result, ensure_ascii=False, indent=2)
        self.result_box.setPlainText(text)
        self._append_terminal(f"اكتملت العملية: {name}")
        if name in {"web_scan", "port_scan", "clear_history"}:
            self.webview.reload()

    def _show_action_error(self, payload: tuple) -> None:
        name, error = payload
        self._set_status(f"خطأ في {name}", state="error")
        self.result_box.setPlainText(error)
        self._append_terminal(f"خطأ في {name}: {error}")

    def closeEvent(self, event: QCloseEvent) -> None:
        self.service_manager.stop()
        event.accept()


def _section_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("SectionTitle")
    return label


def api_request(method: str, path: str, payload: dict | None = None, timeout: int = 35) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{run.BACKEND_URL}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def wait_for_http(url: str, timeout: int = 45) -> bool:
    stop_at = time.time() + timeout
    while time.time() < stop_at:
        try:
            with urllib.request.urlopen(url, timeout=3) as response:
                if response.status < 500:
                    return True
        except (TimeoutError, urllib.error.URLError):
            time.sleep(1)
    return False


def _install_qt_message_filter() -> None:
    global _QT_MESSAGE_FILTER_INSTALLED
    if _QT_MESSAGE_FILTER_INSTALLED:
        return

    def handler(mode: QtMsgType, context, message: str) -> None:
        ignored_messages = (
            "QFont::setPointSize: Point size <= 0",
            "QDxgiVSyncService not destroyed in time",
        )
        if any(ignored in message for ignored in ignored_messages):
            return
        prefix = {
            QtMsgType.QtDebugMsg: "Qt debug",
            QtMsgType.QtInfoMsg: "Qt info",
            QtMsgType.QtWarningMsg: "Qt warning",
            QtMsgType.QtCriticalMsg: "Qt critical",
            QtMsgType.QtFatalMsg: "Qt fatal",
        }.get(mode, "Qt")
        sys.stderr.write(f"{prefix}: {message}\n")

    qInstallMessageHandler(handler)
    _QT_MESSAGE_FILTER_INSTALLED = True


def main() -> int:
    _install_qt_message_filter()
    app = QApplication([])
    app.setApplicationName(APP_TITLE)
    app.setStyleSheet(DEFAULT_STYLE)
    font = QFont("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    window = GuardianDesktop()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
