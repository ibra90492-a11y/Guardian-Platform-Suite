import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import axios from "axios";
import {
  Activity,
  Download,
  FileText,
  Globe,
  Radar,
  ShieldCheck,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import "./styles.css";

const API = "http://localhost:8000";

function App() {
  const [status, setStatus] = useState({ status: "checking", nmap_available: false, nmap_usable: false });
  const [input, setInput] = useState("http://127.0.0.1:8000");
  const [plan, setPlan] = useState(null);
  const [result, setResult] = useState(null);
  const [busy, setBusy] = useState(false);
  const [reportMessage, setReportMessage] = useState("");
  const [scanDialogOpen, setScanDialogOpen] = useState(false);
  const [approvalStep, setApprovalStep] = useState("confirm");
  const [approvalCode, setApprovalCode] = useState("");
  const [approvalMessage, setApprovalMessage] = useState("");

  useEffect(() => {
    axios.get(`${API}/status`).then((response) => setStatus(response.data)).catch(() => {
      setStatus({ status: "offline", nmap_available: false, nmap_usable: false });
    });
  }, []);

  const chartData = useMemo(() => {
    const ports = result?.ports || result?.execution_results?.[0]?.result?.ports || [];
    if (!ports.length) {
      const findings = result?.findings || result?.execution_results?.[0]?.result?.findings || [];
      return [
        { name: "Present", value: findings.filter((item) => item.present).length },
        { name: "Missing", value: findings.filter((item) => !item.present).length },
      ];
    }
    return ports.map((port) => ({ name: `${port.port}/${port.protocol}`, value: port.state === "open" ? 1 : 0 }));
  }, [result]);

  async function understand() {
    setBusy(true);
    setReportMessage("");
    try {
      const response = await axios.post(`${API}/understand`, { user_input: `افحص موقع ${input}`, approved: false });
      setPlan(response.data);
    } finally {
      setBusy(false);
    }
  }

  function openScanDialog() {
    setReportMessage("");
    setApprovalStep("confirm");
    setApprovalCode("");
    setApprovalMessage("");
    setScanDialogOpen(true);
  }

  function closeScanDialog() {
    setScanDialogOpen(false);
    setApprovalStep("confirm");
    setApprovalCode("");
    setApprovalMessage("");
  }

  function acceptAuthorizationQuestion() {
    setApprovalStep("approval");
    setApprovalMessage("");
  }

  function confirmApprovalCode() {
    setApprovalMessage("سيتم لاحقا تحديث الزر");
  }

  async function downloadFullReport() {
    setBusy(true);
    setReportMessage("");
    try {
      const response = await axios.post(`${API}/reports/all/pdf/download-open`);
      setReportMessage(`تم حفظ التقرير في التنزيلات وفتح الملف تلقائيًا: ${response.data.report_path}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <ShieldCheck size={30} />
          <div>
            <strong>Guardian</strong>
            <span>Cyber Assessment</span>
          </div>
        </div>
        <nav>
          <a className="active"><Activity size={18} /> Dashboard / لوحة التحكم</a>
          <a><Globe size={18} /> Website Link / رابط الموقع</a>
          <a><Radar size={18} /> Scanner / الفاحص</a>
          <a><FileText size={18} /> Reports / التقارير</a>
        </nav>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div>
            <h1>لوحة التحكم الأمنية</h1>
            <p>نسخة MVP للعرض على الشركات، مهيأة للفحص الآمن داخل المختبر أو الشبكات المصرح بها.</p>
          </div>
          <div className={`status ${status.status}`}>
            <span></span>
            API {status.status} · Nmap {status.nmap_usable ? "ready" : status.nmap_available ? "fallback" : "missing"}
          </div>
        </header>

        <section className="metrics">
          <Metric icon={<Globe />} label="Website Link" value="رابط الموقع" />
          <Metric icon={<Radar />} label="Port Scan" value={status.nmap_usable ? "Nmap ready" : "Safe fallback"} />
          <Metric icon={<Globe />} label="Web Scan" value="Headers" />
          <Metric icon={<FileText />} label="Reports" value="PDF export" />
        </section>

        <section className="grid">
          <div className="panel operator-panel">
            <div className="panel-title">
              <h2>Website Link رابط الموقع</h2>
              <span>أدخل رابط الموقع المطلوب فحصه</span>
            </div>
            <input
              className="website-link-input"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="https://example.com"
              dir="ltr"
            />
            <div className="actions">
              <button onClick={understand} disabled={busy}>
                <Globe size={17} /> Analyze / تحليل الرابط
              </button>
              <button className="primary" onClick={openScanDialog} disabled={busy}>
                <Globe size={17} /> Web Scan / فحص الموقع
              </button>
              <button className="report-button" onClick={downloadFullReport} disabled={busy}>
                <Download size={17} /> PDF Report / تنزيل التقرير
              </button>
            </div>
            {reportMessage && <div className="report-note">{reportMessage}</div>}
          </div>

          <div className="panel">
            <div className="panel-title">
              <h2>الخطة</h2>
              <span>{plan?.risk_level || "waiting"}</span>
            </div>
            <pre>{plan ? JSON.stringify(plan, null, 2) : "اضغط فهم الطلب لعرض خطة التنفيذ."}</pre>
          </div>

          <div className="panel result-panel">
            <div className="panel-title">
              <h2>النتائج</h2>
              <span>{result ? "updated" : "empty"}</span>
            </div>
            <pre>{result ? JSON.stringify(result, null, 2) : "لم يتم تشغيل فحص بعد."}</pre>
          </div>

          <div className="panel chart-panel">
            <div className="panel-title">
              <h2>ملخص بصري</h2>
              <span>scan signal</span>
            </div>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="name" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" fill="#2f80ed" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      </section>
      {scanDialogOpen && (
        <div className="modal-backdrop" role="presentation">
          <section className="approval-modal" role="dialog" aria-modal="true" aria-labelledby="approval-title">
            {approvalStep === "confirm" ? (
              <>
                <div className="modal-title">
                  <ShieldCheck size={22} />
                  <h2 id="approval-title">تأكيد الموافقة</h2>
                </div>
                <p className="modal-question">
                  هل لديك موافقة من صاحب الموقع أو الشركة أو المؤسسة بفحص الموقع؟
                </p>
                <div className="modal-actions">
                  <button className="primary" onClick={acceptAuthorizationQuestion}>
                    Yes / نعم
                  </button>
                  <button onClick={closeScanDialog}>No / لا</button>
                </div>
              </>
            ) : (
              <>
                <div className="modal-title">
                  <ShieldCheck size={22} />
                  <h2 id="approval-title">رقم الموافقة</h2>
                </div>
                <label className="approval-label" htmlFor="approval-code">
                  أدخل رقم الموافقة
                </label>
                <input
                  id="approval-code"
                  className="approval-input"
                  value={approvalCode}
                  onChange={(event) => setApprovalCode(event.target.value)}
                  placeholder="مثال: APPROVAL-2026/CLIENT-01"
                  autoFocus
                />
                {approvalMessage && <div className="approval-message">{approvalMessage}</div>}
                <div className="modal-actions">
                  <button className="primary" onClick={confirmApprovalCode} disabled={!approvalCode.trim()}>
                    Confirm / موافق
                  </button>
                  <button onClick={closeScanDialog}>Cancel / إلغاء</button>
                </div>
              </>
            )}
          </section>
        </div>
      )}
    </main>
  );
}

function Metric({ icon, label, value }) {
  return (
    <div className="metric">
      <div className="metric-icon">{icon}</div>
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);
