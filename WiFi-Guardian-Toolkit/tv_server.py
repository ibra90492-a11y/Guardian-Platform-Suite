#!/usr/bin/env python3
import http.server
import socketserver
import subprocess
import urllib.parse
import json
import os

PORT = 8080
TV_IP = "192.168.1.3"  # IP التلفزيون

class TVControlHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/control':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # واجهة تحكم HTML بسيطة
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>🎮 TV Remote Control</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {
                        background: linear-gradient(135deg, #1a1a2e, #0f0f1a);
                        color: #0f0;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        text-align: center;
                        padding: 20px;
                    }
                    .remote {
                        display: grid;
                        grid-template-columns: repeat(3, 1fr);
                        gap: 10px;
                        max-width: 300px;
                        margin: 0 auto;
                    }
                    button {
                        background: #0d0d0d;
                        border: 2px solid #0f0;
                        color: #0f0;
                        font-size: 20px;
                        padding: 15px;
                        border-radius: 10px;
                        cursor: pointer;
                        transition: 0.3s;
                    }
                    button:hover {
                        background: #0f0;
                        color: #000;
                        transform: scale(1.05);
                    }
                    .status {
                        margin-top: 20px;
                        padding: 10px;
                        background: #0a0a0a;
                        border-radius: 5px;
                    }
                </style>
            </head>
            <body>
                <h1>🎮 TV Remote Control</h1>
                <div class="remote">
                    <button onclick="sendCommand('keyevent', 'KEYCODE_DPAD_UP')">⬆️</button>
                    <button onclick="sendCommand('keyevent', 'KEYCODE_DPAD_DOWN')">⬇️</button>
                    <button onclick="sendCommand('keyevent', 'KEYCODE_DPAD_LEFT')">⬅️</button>
                    <button onclick="sendCommand('keyevent', 'KEYCODE_DPAD_RIGHT')">➡️</button>
                    <button onclick="sendCommand('keyevent', 'KEYCODE_ENTER')">✅ OK</button>
                    <button onclick="sendCommand('keyevent', 'KEYCODE_BACK')">🔙 Back</button>
                    <button onclick="sendCommand('keyevent', 'KEYCODE_HOME')">🏠 Home</button>
                    <button onclick="sendCommand('app', 'netflix')">📺 Netflix</button>
                    <button onclick="sendCommand('app', 'youtube')">📹 YouTube</button>
                    <button onclick="sendCommand('keyevent', 'KEYCODE_VOLUME_UP')">🔊 +</button>
                    <button onclick="sendCommand('keyevent', 'KEYCODE_VOLUME_DOWN')">🔉 -</button>
                    <button onclick="sendCommand('keyevent', 'KEYCODE_MUTE')">🔇 Mute</button>
                </div>
                <div class="status" id="status">✅ جاهز للتحكم</div>
                
                <script>
                    function sendCommand(type, value) {
                        fetch('/api/command', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({type: type, value: value})
                        })
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('status').innerHTML = '✅ ' + data.message;
                        })
                        .catch(error => {
                            document.getElementById('status').innerHTML = '❌ خطأ: ' + error;
                        });
                    }
                </script>
            </body>
            </html>
            '''
            self.wfile.write(html.encode())
            
        elif self.path.startswith('/api/command'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            # معالجة الأمر
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            result = self.execute_command(data)
            self.wfile.write(json.dumps({"message": result}).encode())
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def execute_command(self, data):
        """تنفيذ الأمر على التلفزيون"""
        cmd_type = data.get('type')
        value = data.get('value')
        
        try:
            if cmd_type == 'keyevent':
                # إرسال أمر ADB
                result = subprocess.run(
                    ['adb', 'shell', 'input', 'keyevent', value],
                    capture_output=True, text=True, timeout=5
                )
                return f"تم إرسال الأمر: {value}"
                
            elif cmd_type == 'app':
                # فتح تطبيق معين
                apps = {
                    'netflix': 'com.netflix.ninja/.MainActivity',
                    'youtube': 'com.google.android.youtube.tv/.MainActivity',
                    'prime': 'com.amazon.amazonvideo.livingroom/.MainActivity'
                }
                if value in apps:
                    subprocess.run(
                        ['adb', 'shell', 'am', 'start', '-n', apps[value]],
                        capture_output=True, timeout=5
                    )
                    return f"تم فتح {value}"
                return f"تطبيق {value} غير معروف"
            
            return "تم التنفيذ"
        except Exception as e:
            return f"خطأ: {e}"
    
    def log_message(self, format, *args):
        pass  # تعطيل رسائل السجل للتشغيل النظيف

# تشغيل الخادم
if __name__ == '__main__':
    # التأكد من اتصال ADB
    subprocess.run(['adb', 'connect', f'{TV_IP}:5555'], capture_output=True)
    
    with socketserver.TCPServer(("", PORT), TVControlHandler) as httpd:
        print(f"🌐 خادم التحكم يعمل على http://localhost:{PORT}")
        print(f"📺 عنوان التلفزيون: {TV_IP}")
        print("✅ انتظر حتى يفتح التلفزيون الرابط")
        httpd.serve_forever()