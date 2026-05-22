# Guardian Cyber Assessment Platform

MVP for a defensive cyber assessment dashboard.

## Run Desktop App

The main project entry point now opens a desktop window. The left half is the native Guardian control form, and the right half embeds the web dashboard inside the same form.

```powershell
.\.venv\Scripts\python.exe main.py
```

Or double-click:

```powershell
.\run_desktop.bat
```

The launcher installs the desktop WebView dependency from `desktop_requirements.txt` when needed.

Guardian uses the built-in safe socket fallback for port checks by default. This avoids Windows system popups from incomplete Nmap installations. To opt in to Nmap explicitly, set `GUARDIAN_ENABLE_NMAP=1` before launching the app.

## Merged Workspace

This folder now also contains the WiFi Guardian Toolkit under `WiFi-Guardian-Toolkit/`.
The default main form for this merged workspace is still the Guardian platform desktop form launched through `main.py` -> `run_desktop.py` -> `desktop_app.py`.

## Run Web Services Only

Backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Frontend:

```powershell
& "C:\Users\3D\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" .\frontend\node_modules\vite\bin\vite.js --host 127.0.0.1 --port 5173
```

Open:

- API: http://localhost:8000/docs
- Dashboard: http://localhost:5173

Use only on systems you own or have written permission to assess.
