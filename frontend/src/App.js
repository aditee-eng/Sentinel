import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE = 'http://localhost:8000/api';

const PROGRESS_STEPS = [
  [10, 'Spawning parallel agents...'],
  [30, 'Fetching GitHub releases...'],
  [50, 'Scanning news sources...'],
  [70, 'Scraping pricing pages...'],
  [90, 'Generating LLM reports...'],
  [100, 'All agents finished.'],
];

function Clock() {
  const [time, setTime] = useState('');

  useEffect(() => {
    const tick = () => {
      const now = new Date();
      let h = now.getHours();
      const m = now.getMinutes().toString().padStart(2, '0');
      const ampm = h >= 12 ? 'PM' : 'AM';
      h = h % 12 || 12;
      setTime(`${h}:${m} ${ampm}`);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  return <div className="clock">{time}</div>;
}

function App() {
  const [competitors, setCompetitors] = useState([]);
  const [reports, setReports] = useState({});
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [progressMsg, setProgressMsg] = useState('');
  const [statusText, setStatusText] = useState('Ready');
  const [statusMode, setStatusMode] = useState('ready');

  useEffect(() => {
    fetchAll();
  }, []);

  const fetchAll = async () => {
    try {
      const res = await axios.get(`${API_BASE}/competitors`);
      const list = res.data.competitors;
      setCompetitors(list);

      const reportMap = {};
      await Promise.all(
        list.map(async (c) => {
          const r = await axios.get(`${API_BASE}/reports/${c}`);
          reportMap[c] = r.data;
        })
      );
      setReports(reportMap);
    } catch (err) {
      setStatusText('Error loading data');
      setStatusMode('error');
    }
  };

  const runSentinel = async () => {
    setRunning(true);
    setStatusMode('running');
    setStatusText('Running...');
    setProgress(0);

    // animate progress bar while API call runs
    let step = 0;
    const interval = setInterval(() => {
      if (step < PROGRESS_STEPS.length - 1) {
        const [pct, msg] = PROGRESS_STEPS[step];
        setProgress(pct);
        setProgressMsg(msg);
        step++;
      }
    }, 700);

    try {
      const res = await axios.post(`${API_BASE}/run`);
      clearInterval(interval);
      setProgress(100);
      setProgressMsg('All agents finished. Reports updated.');
      setStatusText('Done');
      setStatusMode('ready');

      const newReports = {};
      res.data.reports.forEach((r) => {
        newReports[r.competitor] = { report: r.report };
      });
      setReports(newReports);
    } catch (err) {
      clearInterval(interval);
      setStatusText('Error');
      setStatusMode('error');
      setProgressMsg('Something went wrong. Check your terminal.');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="desktop">
      <div className="window">
        <div className="titlebar">
          <div className="titlebar-title">
            <div className="titlebar-icon">S</div>
            Sentinel v1.0 — Competitive Intelligence System
          </div>
          <div className="titlebar-buttons">
            <div className="win-btn">_</div>
            <div className="win-btn">□</div>
            <div className="win-btn">✕</div>
          </div>
        </div>

        <div className="menubar">
          {['File', 'View', 'Run', 'Competitors', 'Help'].map((m) => (
            <div className="menu-item" key={m}>{m}</div>
          ))}
        </div>

        <div className="toolbar">
          <button
            className="toolbar-btn"
            onClick={runSentinel}
            disabled={running}
          >
            ▶ Run Sentinel
          </button>
          <div className="divider" />
          <button className="toolbar-btn" onClick={fetchAll} disabled={running}>
            ⟳ Refresh
          </button>
          <div className="divider" />
          <span style={{ fontSize: 14, color: '#000080' }}>
            <span className={`status-light ${statusMode}`} />
            {statusText}
          </span>
        </div>

        <div className="window-body">
          {(running || progress > 0) && (
            <div className="inset-box">
              <div className="section-label">Agent activity log</div>
              <div className="progress-bar-outer">
                <div
                  className="progress-bar-inner"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <div style={{ fontSize: 14, color: '#000', marginTop: 4 }}>
                {progressMsg}
              </div>
            </div>
          )}

          <div className="section-label">
            TRACKED COMPETITORS — {competitors.length} ACTIVE
          </div>

          <div className="competitor-grid">
            {competitors.map((c) => (
              <div className="competitor-card" key={c}>
                <div className="card-header">
                  📁 {c.toUpperCase()}
                </div>
                <div className="card-body">
                  {reports[c]?.report || 'No report yet — click Run Sentinel.'}
                </div>
                <div className="card-footer">
                  <span>
                    {reports[c]?.last_findings_count
                      ? `${reports[c].last_findings_count} findings`
                      : 'No data yet'}
                  </span>
                  <span>GitHub · News · Pricing</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="taskbar">
        <div className="start-btn">⊞ Start</div>
        <div style={{
          background: '#c0c0c0',
          borderTop: '2px solid #808080',
          borderLeft: '2px solid #808080',
          borderRight: '2px solid #fff',
          borderBottom: '2px solid #fff',
          padding: '2px 12px',
          fontSize: 15
        }}>
          📊 Sentinel
        </div>
        <Clock />
      </div>
    </div>
  );
}

export default App;