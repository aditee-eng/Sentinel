import { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import StatsPanel from './StatsPanel';

const API_BASE = `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api`;

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
  const [stats, setStats] = useState([]);

  useEffect(() => {
    fetchAll();
  }, []);

 const fetchAll = async () => {
    try {
      console.log('fetchAll called');
      const res = await axios.get(`${API_BASE}/competitors`);
      console.log('competitors:', res.data);
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

      const statsRes = await axios.get(`${API_BASE}/stats`);
      setStats(statsRes.data.stats);
      console.log('fetchAll done');

    } catch (err) {
      console.error('fetchAll error:', err);
      setStatusText('Error loading data');
      setStatusMode('error');
    }
  };
   

  const runSentinel = async () => {
    setRunning(true);
    setStatusMode('running');
    setStatusText('Running...');
    setProgress(0);

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
      await axios.post(`${API_BASE}/run`);
      clearInterval(interval);
      setProgress(100);
      setProgressMsg('All agents finished. Reports updated.');
      setStatusText('Done');
      setStatusMode('ready');
      await fetchAll();
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
            <div class="titlebar-icon">S</div>
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
          <button className="toolbar-btn" onClick={fetchAll}>
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

          <StatsPanel stats={stats} />

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
                  {reports[c]?.report
                    ? reports[c].report.split('\n').filter(l => l.trim()).map((line, i) => (
                     <div key={i} style={{ marginBottom: 4 }}>
                       {line.trim()}
                     </div>
                    ))
                  : 'No report yet — click Run Sentinel.'}
                </div>
                <div className="card-footer">
                 <span>
                   {stats.find(s => s.competitor === c)?.new_this_run > 0
                     ? `${stats.find(s => s.competitor === c)?.new_this_run} new this week`
                     : 'No new updates this week'}
                  </span>
                 <span>News · Pricing</span>
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