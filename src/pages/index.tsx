import { useEffect, useMemo, useState, type CSSProperties } from 'react';

const API_BASE = process.env.NEXT_PUBLIC_GREENBYTE_API || 'http://127.0.0.1:5000';
const POLL_MS = 2000;

type ImpactRecord = {
  session_id: string;
  source_id: string;
  prompt_preview: string;
  model: string;
  device: string;
  energy_source: string;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  local_energy_j: number;
  cloud_energy_j: number;
  cloud_carbon_g: number;
  local_carbon_g: number;
  verification_overhead_g: number;
  net_avoided_g: number;
  reduction_pct: number;
  methodology_version: string;
  baseline_origin: string;
  local_measurement_origin: string;
  local_duration_s?: number;
  local_average_gpu_w?: number;
  local_peak_gpu_w?: number;
  cloud_provider?: string;
  cloud_model?: string;
  cloud_input_tokens?: number;
  cloud_output_tokens?: number;
  cloud_total_tokens?: number;
  cloud_duration_s?: number;
  cloud_energy_origin?: string;
  certificate_id: string;
  proof_hash: string;
  block_index: number;
  verified_at: string;
  certificate_url?: string;
  proof_url?: string;
  verify_url?: string;
};

type DashboardResponse = {
  status: string;
  source_live: boolean;
  source_last_seen_seconds: number | null;
  source_name: string;
  latest: ImpactRecord | null;
  history: ImpactRecord[];
  totals: {
    sessions: number;
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
    local_energy_j: number;
    cloud_energy_j: number;
    avoided_carbon_g: number;
  };
  chain: {
    name: string;
    mode: string;
    height: number;
    valid: boolean;
  };
  methodology: {
    version: string;
    acu_definition: string;
  };
};

const emptyDashboard: DashboardResponse = {
  status: 'offline',
  source_live: false,
  source_last_seen_seconds: null,
  source_name: 'Friend AI Runtime',
  latest: null,
  history: [],
  totals: {
    sessions: 0,
    input_tokens: 0,
    output_tokens: 0,
    total_tokens: 0,
    local_energy_j: 0,
    cloud_energy_j: 0,
    avoided_carbon_g: 0,
  },
  chain: {
    name: 'GreenByte Ledger PoC',
    mode: 'single-node hash chain',
    height: 0,
    valid: true,
  },
  methodology: {
    version: 'GB-CARBON-v1.0',
    acu_definition: '1 ACU = 1 g CO₂e net avoided versus the configured cloud baseline',
  },
};

function fmt(value: number, digits = 3) {
  if (!Number.isFinite(value)) return '—';
  if (Math.abs(value) >= 1000) return value.toLocaleString(undefined, { maximumFractionDigits: 0 });
  return value.toFixed(digits);
}

function fmtCarbon(value: number) {
  if (!Number.isFinite(value)) return '—';
  if (value > 0 && value < 0.0001) return '<0.0001 g';
  return `${value.toFixed(4)} g`;
}

function fmtTime(value?: string) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function shortHash(value?: string, left = 10, right = 8) {
  if (!value) return '—';
  if (value.length <= left + right + 3) return value;
  return `${value.slice(0, left)}…${value.slice(-right)}`;
}

function Icon({ name }: { name: 'leaf' | 'pulse' | 'cloud' | 'phone' | 'shield' | 'certificate' | 'chain' | 'spark' | 'sun' | 'bars' | 'drop' | 'globe' }) {
  const common = { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', strokeWidth: 1.8, strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const };
  const paths: Record<string, JSX.Element> = {
    leaf: <><path d="M20 4C13 4 6.5 6.6 4.2 12.1c-1.2 2.8-.6 5.4 1.4 7.2 1.3-4.7 4.4-8.1 9.5-10.2-4 2.4-6.7 5.4-8 9.1 5.9 1.2 10.5-2.5 12.1-7.5C20 8.4 20.2 6.1 20 4Z" /></>,
    pulse: <><path d="M3 12h4l2-5 4 10 2-5h6" /></>,
    cloud: <><path d="M7 18h10a4 4 0 0 0 .7-7.9A6 6 0 0 0 6.2 8.6 4.5 4.5 0 0 0 7 18Z" /></>,
    phone: <><rect x="7" y="2.8" width="10" height="18.4" rx="2.2" /><path d="M10 5h4M11 18.2h2" /></>,
    shield: <><path d="M12 3 19 6v5c0 4.7-2.7 8-7 10-4.3-2-7-5.3-7-10V6l7-3Z" /><path d="m9.2 12 1.8 1.8 3.8-4" /></>,
    certificate: <><path d="M6 3h9l3 3v10H6V3Z" /><path d="M15 3v4h4M9 9h5M9 12h6" /><circle cx="12" cy="18.2" r="2.1" /></>,
    chain: <><path d="M9.5 14.5 8 16a3 3 0 1 1-4.2-4.2l3-3A3 3 0 0 1 11 9" /><path d="M14.5 9.5 16 8a3 3 0 1 1 4.2 4.2l-3 3A3 3 0 0 1 13 15" /><path d="m8.5 15.5 7-7" /></>,
    spark: <><path d="m12 2 1.8 5.2L19 9l-5.2 1.8L12 16l-1.8-5.2L5 9l5.2-1.8L12 2Z" /><path d="m18 15 .8 2.2L21 18l-2.2.8L18 21l-.8-2.2L15 18l2.2-.8L18 15Z" /></>,
    sun: <><circle cx="12" cy="12" r="4" /><path d="M12 2v2.2M12 19.8V22M4.9 4.9l1.5 1.5M17.6 17.6l1.5 1.5M2 12h2.2M19.8 12H22M4.9 19.1l1.5-1.5M17.6 6.4l1.5-1.5" /></>,
    bars: <><path d="M5 19V9M12 19V5M19 19v-8" /></>,
    drop: <><path d="M12 3s5 5.2 5 9a5 5 0 1 1-10 0c0-3.8 5-9 5-9Z" /></>,
    globe: <><circle cx="12" cy="12" r="9" /><path d="M3 12h18M12 3a15 15 0 0 1 0 18M12 3a15 15 0 0 0 0 18" /></>,
  };
  return <svg {...common}>{paths[name]}</svg>;
}

export default function Home() {
  const [dashboard, setDashboard] = useState<DashboardResponse>(emptyDashboard);
  const [backendOnline, setBackendOnline] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const [selected, setSelected] = useState<ImpactRecord | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/dashboard`, { cache: 'no-store' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data: DashboardResponse = await res.json();
        if (!active) return;
        setDashboard(data);
        setBackendOnline(true);
        setLastRefresh(new Date());
        setSelected((current) => current || data.latest);
      } catch {
        if (!active) return;
        setBackendOnline(false);
      }
    };

    load();
    const timer = window.setInterval(load, POLL_MS);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  useEffect(() => {
    if (dashboard.latest) setSelected(dashboard.latest);
  }, [dashboard.latest?.certificate_id]);

  const latest = dashboard.latest;
  const localShare = useMemo(() => {
    if (!latest || latest.cloud_carbon_g <= 0) return 0;
    return Math.min(100, Math.max(0, (latest.local_carbon_g / latest.cloud_carbon_g) * 100));
  }, [latest]);

  const reduction = latest?.reduction_pct ?? 0;
  const ringStyle = { '--progress': `${Math.max(0, Math.min(100, reduction)) * 3.6}deg` } as CSSProperties;

  const copyCertificate = async () => {
    if (!selected?.certificate_id) return;
    try {
      await navigator.clipboard.writeText(selected.certificate_id);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      setCopied(false);
    }
  };

  return (
    <main className="gb5-app">
      <div className="gb5-glow glow-a" />
      <div className="gb5-glow glow-b" />
      <div className="gb5-noise" />

      <div className="gb5-shell">
        <header className="gb5-topbar">
          <div className="brand-lockup">
            <span className="brand-mark"><Icon name="leaf" /></span>
            <span className="brand-copy"><strong>GreenByte</strong><small>Prompt Carbon Measurement & Verification</small></span>
          </div>

          <nav className="poster-nav" aria-label="section navigation">
            <a href="#measure">Measure</a>
            <a href="#compare">Compare</a>
            <a href="#verify">Verify</a>
            <a href="#methodology">Methodology</a>
          </nav>

          <div className="system-strip">
            <div className={`system-chip ${backendOnline ? 'live' : 'down'}`}>
              <span className="status-dot" />
              <span><b>{backendOnline ? 'ENGINE ONLINE' : 'ENGINE OFFLINE'}</b><small>Carbon engine</small></span>
            </div>
            <div className={`system-chip ${dashboard.source_live ? 'live' : 'idle'}`}>
              <span className="status-dot" />
              <span><b>{dashboard.source_live ? 'AI CONNECTED' : 'WAITING FOR AI'}</b><small>{dashboard.source_name}</small></span>
            </div>
            <div className={`system-chip ${dashboard.chain.valid ? 'live' : 'down'}`}>
              <span className="status-dot" />
              <span><b>{dashboard.chain.valid ? 'PROOF READY' : 'LEDGER ERROR'}</b><small>Block {dashboard.chain.height}</small></span>
            </div>
          </div>
        </header>

        <section className="hero-grid hero-poster">
          <div className="hero-copy">
            <p className="eyebrow"><span /> BUILD SOLUTIONS. DRIVE IMPACT. SHAPE A SUSTAINABLE AI FUTURE.</p>
            <div className="hero-kicker">Blockchain + AI for Carbon Transparency</div>
            <h1>Every Prompt Has a <br /><em>Carbon Cost.</em></h1>
            <h2>Measure it. Compare it. Verify what local AI saves.</h2>
            <p className="hero-sub">GreenByte connects to your friend's AI runtime in the background, captures real input and output telemetry, compares cloud and local edge carbon impact, and turns the difference into a verifiable sustainability record.</p>

            <div className="cta-band">
              <div className="cta-pill"><Icon name="pulse" /> Prompt telemetry from AI runtime</div>
              <div className="cta-pill"><Icon name="cloud" /> Cloud baseline comparison</div>
              <div className="cta-pill"><Icon name="shield" /> Verified impact certificate</div>
            </div>

            <div className="hero-points">
              <div><b>Carbon Transparency</b><span>Prompt-level AI footprint measurement</span></div>
              <div><b>Data Integrity</b><span>Tamper-evident proof and certificate trail</span></div>
              <div><b>Renewable Edge</b><span>Solar-powered repurposed device inference</span></div>
            </div>
          </div>

          <div className="impact-hero-card">
            <div className="impact-card-head">
              <div>
                <small>LIVE IMPACT SNAPSHOT</small>
                <strong>{dashboard.source_live ? 'CONNECTED SESSION' : 'STANDBY MODE'}</strong>
              </div>
              <span className="impact-chip">{dashboard.methodology.version}</span>
            </div>

            <div className="impact-ring" style={ringStyle}>
              <div className="impact-ring-inner">
                <small>NET AVOIDED</small>
                <strong>{latest ? fmt(latest.net_avoided_g, 4) : '—'}</strong>
                <span>g CO₂e · ACU</span>
              </div>
            </div>

            <div className="impact-three-up">
              <div><span>Reduction</span><strong>{latest ? `${fmt(latest.reduction_pct, 1)}%` : '—'}</strong></div>
              <div><span>Cloud footprint</span><strong>{latest ? `${fmt(latest.cloud_carbon_g, 4)} g` : '—'}</strong></div>
              <div><span>Local footprint</span><strong>{latest ? fmtCarbon(latest.local_carbon_g) : '—'}</strong></div>
            </div>

            <div className="hero-record-bar">
              <span>Latest verified session</span>
              <b>{latest ? shortHash(latest.session_id, 8, 6) : 'Waiting for AI runtime'}</b>
            </div>
          </div>
        </section>

        <section className="focus-grid" id="measure">
          <article className="focus-card highlight">
            <div className="focus-top"><span>01</span><b>GreenByte Edge Node</b></div>
            <h3>Solar-powered old phone</h3>
            <p>Repurpose an old smartphone as a local AI node and capture measured edge telemetry from real inference sessions.</p>
            <ul>
              <li><Icon name="phone" /> Local AI inference</li>
              <li><Icon name="sun" /> Solar-assisted energy source</li>
              <li><Icon name="bars" /> Measured device energy</li>
            </ul>
          </article>

          <article className="focus-card">
            <div className="focus-top"><span>02</span><b>Cloud Baseline</b></div>
            <h3>Comparable cloud inference</h3>
            <p>Use the same workload telemetry to estimate how much carbon the prompt would produce in a cloud AI environment.</p>
            <ul>
              <li><Icon name="cloud" /> Data-center energy baseline</li>
              <li><Icon name="globe" /> Grid carbon intensity</li>
              <li><Icon name="spark" /> Configured PUE assumptions</li>
            </ul>
          </article>

          <article className="focus-card">
            <div className="focus-top"><span>03</span><b>Carbon Engine</b></div>
            <h3>Calculate avoided carbon</h3>
            <p>GreenByte converts energy into carbon, compares local and cloud paths, and issues ACU based on net avoided emissions.</p>
            <ul>
              <li><Icon name="leaf" /> 1 ACU = 1 g CO₂e avoided</li>
              <li><Icon name="bars" /> Tokens describe workload</li>
              <li><Icon name="pulse" /> Joules drive the footprint</li>
            </ul>
          </article>

          <article className="focus-card">
            <div className="focus-top"><span>04</span><b>Verification Layer</b></div>
            <h3>Issue a shareable certificate</h3>
            <p>Each verified session creates a tamper-evident proof record and a sustainability certificate for transparent reporting.</p>
            <ul>
              <li><Icon name="shield" /> Evidence hash</li>
              <li><Icon name="chain" /> Ledger commitment</li>
              <li><Icon name="certificate" /> Impact certificate</li>
            </ul>
          </article>
        </section>

        <section className="metric-ribbon">
          <div><span>Verified sessions</span><strong>{dashboard.totals.sessions.toLocaleString()}</strong><small>automatic impact records</small></div>
          <div><span>AI workload observed</span><strong>{dashboard.totals.total_tokens.toLocaleString()}</strong><small>input + output tokens</small></div>
          <div><span>Local edge energy</span><strong>{fmt(dashboard.totals.local_energy_j, 1)}</strong><small>joules measured</small></div>
          <div className="accent"><span>Lifetime avoided carbon</span><strong>{fmt(dashboard.totals.avoided_carbon_g, 3)}</strong><small>g CO₂e · ACU</small></div>
        </section>

        <section className="workspace">
          <div className="left-stack">
            <article className="panel live-session-panel" id="compare">
              <div className="panel-head">
                <div><p>LIVE TELEMETRY</p><h2>Inference session from connected AI</h2></div>
                <span className={`live-badge ${dashboard.source_live ? 'on' : ''}`}><i /> {dashboard.source_live ? 'AUTO-INGESTING' : 'AWAITING NEW SESSION'}</span>
              </div>

              {latest ? (
                <>
                  <div className="prompt-preview">
                    <div className="prompt-label"><span>PROMPT PREVIEW</span><b>{latest.model}</b></div>
                    <p>{latest.prompt_preview || 'Prompt content withheld; telemetry received.'}</p>
                  </div>

                  <div className="telemetry-split">
                    <section className="telemetry-lane local-lane">
                      <div className="lane-title"><span>LOCAL TEST</span><b>{latest.model}</b></div>
                      <div className="telemetry-grid">
                        <div><span>Input tokens</span><strong>{latest.input_tokens}</strong><small>Ollama Local</small></div>
                        <div><span>Output tokens</span><strong>{latest.output_tokens}</strong><small>generated locally</small></div>
                        <div><span>GPU energy</span><strong>{fmt(latest.local_energy_j, 3)} J</strong><small>telemetry-derived</small></div>
                        <div><span>Runtime</span><strong>{fmt(latest.local_duration_s || 0, 3)} s</strong><small>{latest.device}</small></div>
                      </div>
                    </section>

                    <section className="telemetry-lane cloud-lane">
                      <div className="lane-title"><span>CLOUD TEST</span><b>{latest.cloud_model || 'Cloud baseline'}</b></div>
                      <div className="telemetry-grid">
                        <div><span>Input tokens</span><strong>{latest.cloud_input_tokens ?? '—'}</strong><small>{latest.cloud_provider || 'Cloud provider'}</small></div>
                        <div><span>Output tokens</span><strong>{latest.cloud_output_tokens ?? '—'}</strong><small>cloud completion</small></div>
                        <div><span>Cloud energy</span><strong>{fmt(latest.cloud_energy_j, 1)} J</strong><small>testing estimate</small></div>
                        <div><span>Runtime</span><strong>{fmt(latest.cloud_duration_s || 0, 3)} s</strong><small>{latest.cloud_energy_origin || 'estimated baseline'}</small></div>
                      </div>
                    </section>
                  </div>
                </>
              ) : (
                <div className="waiting-state">
                  <span className="waiting-icon"><Icon name="pulse" /></span>
                  <h3>Waiting for your friend's AI</h3>
                  <p>As soon as the AI adapter sends input tokens, output tokens and energy telemetry, GreenByte will measure the session automatically.</p>
                </div>
              )}
            </article>

            <article className="panel comparison-panel">
              <div className="panel-head">
                <div><p>CARBON COMPARISON</p><h2>Cloud AI vs local edge AI</h2></div>
                <span className="method-chip">{dashboard.methodology.version}</span>
              </div>

              <div className="comparison-stage">
                <div className="compare-side cloud-side">
                  <span className="compare-icon"><Icon name="cloud" /></span>
                  <div><small>CLOUD AI BASELINE</small><strong>{latest ? `${fmt(latest.cloud_carbon_g, 4)} g` : '—'}</strong><p>{latest?.baseline_origin || 'Configured cloud reference'}</p></div>
                </div>

                <div className="differential-core">
                  <div className="difference-value"><small>NET AVOIDED CARBON</small><strong>{latest ? fmt(latest.net_avoided_g, 4) : '—'}</strong><span>g CO₂e · ACU</span></div>
                  <div className="difference-arrow">↓</div>
                  <div className="reduction-number"><strong>{latest ? `${fmt(latest.reduction_pct, 1)}%` : '—'}</strong><small>lower than cloud</small></div>
                </div>

                <div className="compare-side local-side">
                  <span className="compare-icon"><Icon name="phone" /></span>
                  <div><small>LOCAL EDGE NODE</small><strong>{latest ? fmtCarbon(latest.local_carbon_g) : '—'}</strong><p>{latest?.energy_source || 'Measured on device'}</p></div>
                </div>
              </div>

              <div className="bar-lab">
                <div className="bar-line"><span>Cloud AI</span><div className="track"><i className="cloud-fill" style={{ width: latest ? '100%' : '0%' }} /></div><b>{latest ? fmt(latest.cloud_carbon_g, 4) : '—'}</b></div>
                <div className="bar-line"><span>Local edge</span><div className="track"><i className="local-fill" style={{ width: latest ? `${Math.max(1.5, localShare)}%` : '0%' }} /></div><b>{latest ? fmtCarbon(latest.local_carbon_g) : '—'}</b></div>
              </div>
            </article>
          </div>

          <aside className="right-stack" id="verify">
            <article className="panel proof-panel">
              <div className="panel-head">
                <div><p>VERIFICATION PIPELINE</p><h2>Trusted impact record</h2></div>
                <span className={`proof-state ${latest ? 'verified' : ''}`}><i /> {latest ? 'VERIFIED' : 'STANDBY'}</span>
              </div>

              <div className="proof-flow">
                <div className={latest ? 'done' : ''}><span>01</span><section><b>Inference telemetry</b><small>Input + output + measured edge energy</small></section></div>
                <i />
                <div className={latest ? 'done' : ''}><span>02</span><section><b>Carbon calculation</b><small>Cloud vs local methodology engine</small></section></div>
                <i />
                <div className={latest ? 'done' : ''}><span>03</span><section><b>Evidence hashed</b><small>Tamper-evident proof trail</small></section></div>
                <i />
                <div className={latest ? 'done' : ''}><span>04</span><section><b>Certificate issued</b><small>{dashboard.chain.name}</small></section></div>
              </div>

              <div className="certificate-card">
                <div className="cert-top"><span><Icon name="certificate" /> VERIFIED PROMPT IMPACT CERTIFICATE</span><b>{latest ? 'READY' : 'PREVIEW'}</b></div>
                <small>GREENBYTE CERTIFICATION</small>
                <strong className="cert-acu">{latest ? fmt(latest.net_avoided_g, 4) : '—'} <em>ACU</em></strong>
                <p>{dashboard.methodology.acu_definition}</p>
                <div className="cert-grid">
                  <div><span>Certificate ID</span><b>{latest ? shortHash(latest.certificate_id, 12, 7) : 'Generated automatically'}</b></div>
                  <div><span>Block reference</span><b>{latest ? `#${latest.block_index}` : '—'}</b></div>
                  <div><span>Proof hash</span><b>{latest ? shortHash(latest.proof_hash, 12, 7) : '—'}</b></div>
                  <div><span>Verified at</span><b>{latest ? fmtTime(latest.verified_at) : '—'}</b></div>
                </div>
                {latest && (
                  <div className="cert-actions">
                    <a className="cert-action primary" href={`/certificate/${encodeURIComponent(latest.certificate_id)}`}>Open certificate ↗</a>
                    <a className="cert-action" href={`/verify/${encodeURIComponent(latest.certificate_id)}`}>Verify record</a>
                    <button className="cert-action" onClick={copyCertificate}>{copied ? 'Copied ✓' : 'Copy ID'}</button>
                  </div>
                )}
              </div>
            </article>

            <article className="panel methodology-panel" id="methodology">
              <div className="panel-head compact">
                <div><p>METHODOLOGY</p><h2>Transparent assumptions</h2></div>
                <Icon name="spark" />
              </div>
              <div className="formula-stack">
                <div><span>CLOUD CO₂e</span><code>Cloud energy × PUE ÷ 3,600,000 × grid carbon intensity</code></div>
                <div><span>LOCAL CO₂e</span><code>Measured device energy ÷ 3,600,000 × local energy intensity</code></div>
                <div><span>NET ACU</span><code>max(0, Cloud − Local − Verification Overhead)</code></div>
              </div>
              <p className="method-note">GreenByte measures prompt-level sustainability in the background. The dashboard does not ask the user to self-report tokens, carbon or savings.</p>
            </article>
          </aside>
        </section>

        <section className="history-section">
          <div className="section-head">
            <div><p>IMPACT HISTORY</p><h2>Recent verified inference sessions</h2></div>
            <span>{lastRefresh ? `Dashboard refreshed ${lastRefresh.toLocaleTimeString()}` : 'Connecting…'}</span>
          </div>

          <div className="history-table-wrap">
            <table className="history-table">
              <thead><tr><th>Session</th><th>Model</th><th>Tokens</th><th>Local energy</th><th>Cloud CO₂e</th><th>Local CO₂e</th><th>Avoided</th><th>Proof</th><th>Certificate</th><th>Verify</th></tr></thead>
              <tbody>
                {dashboard.history.length > 0 ? dashboard.history.map((record) => (
                  <tr key={record.certificate_id} onClick={() => setSelected(record)} className={selected?.certificate_id === record.certificate_id ? 'selected-row' : ''}>
                    <td><b>{shortHash(record.session_id, 7, 5)}</b><small>{fmtTime(record.verified_at)}</small></td>
                    <td>{record.model}</td>
                    <td>{record.total_tokens}</td>
                    <td>{fmt(record.local_energy_j, 2)} J</td>
                    <td>{fmt(record.cloud_carbon_g, 4)} g</td>
                    <td>{fmtCarbon(record.local_carbon_g)}</td>
                    <td className="good">{fmt(record.net_avoided_g, 4)} ACU</td>
                    <td>
                      <a className="table-link proof-link" href={`/proof/${encodeURIComponent(record.certificate_id)}`} onClick={(e) => e.stopPropagation()}>Block #{record.block_index}</a>
                    </td>
                    <td>
                      <a className="table-link cert-link" href={`/certificate/${encodeURIComponent(record.certificate_id)}`} onClick={(e) => e.stopPropagation()}>{shortHash(record.certificate_id, 10, 5)}</a>
                    </td>
                    <td>
                      <a className="table-link verify-link" href={`/verify/${encodeURIComponent(record.certificate_id)}`} onClick={(e) => e.stopPropagation()}>Verify ↗</a>
                    </td>
                  </tr>
                )) : (
                  <tr className="empty-row"><td colSpan={10}>No records yet. Connect your friend&apos;s AI runtime and GreenByte will populate this automatically.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        <footer>
          <div><Icon name="leaf" /><span><b>GreenByte</b> · Prompt carbon measurement and verification</span></div>
          <p>Measure · Compare · Verify · A Cleaner AI Future</p>
        </footer>
      </div>
    </main>
  );
}
