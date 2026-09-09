import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

const API_BASE = process.env.NEXT_PUBLIC_GREENBYTE_API || 'http://127.0.0.1:5000';

type ApiState = { loading: boolean; error: string; record: any | null; ledgerValid: boolean };

function short(value?: string, left = 14, right = 8) {
  if (!value) return '—';
  if (value.length <= left + right + 3) return value;
  return `${value.slice(0, left)}…${value.slice(-right)}`;
}

function carbon(value?: number) {
  const n = Number(value || 0);
  if (n > 0 && n < 0.0001) return '<0.0001 g';
  return `${n.toFixed(4)} g`;
}

function dt(value?: string) {
  if (!value) return '—';
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString();
}

export default function CertificatePage() {
  const router = useRouter();
  const id = typeof router.query.id === 'string' ? router.query.id : '';
  const [state, setState] = useState<ApiState>({ loading: true, error: '', record: null, ledgerValid: false });
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (!id) return;
    let alive = true;
    fetch(`${API_BASE}/api/certificate/${encodeURIComponent(id)}`, { cache: 'no-store' })
      .then(async (r) => {
        const data = await r.json();
        if (!r.ok) throw new Error(data.error || `HTTP ${r.status}`);
        return data;
      })
      .then((data) => alive && setState({ loading: false, error: '', record: data.record, ledgerValid: !!data.ledger_valid }))
      .catch((e) => alive && setState({ loading: false, error: e.message || 'Unable to load certificate', record: null, ledgerValid: false }));
    return () => { alive = false; };
  }, [id]);

  const copyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {}
  };

  const r = state.record;

  return (
    <main className="verification-page">
      <div className="verification-glow" />
      <div className="verification-shell">
        <header className="verify-topbar">
          <a href="/" className="verify-brand"><span>◒</span><b>GreenByte</b><small>Verification Network</small></a>
          <a href="/" className="back-dashboard">← Back to dashboard</a>
        </header>

        {state.loading && <div className="verify-loading">Loading certificate from GreenByte database…</div>}
        {state.error && <div className="verify-error"><b>Certificate unavailable</b><span>{state.error}</span></div>}

        {r && (
          <>
            <section className="certificate-hero">
              <div className="certificate-status-row">
                <span className="verified-seal">✓ VERIFIED IMPACT CERTIFICATE</span>
                <span className={state.ledgerValid ? 'integrity-ok' : 'integrity-bad'}>{state.ledgerValid ? 'LEDGER INTEGRITY VALID' : 'LEDGER CHECK FAILED'}</span>
              </div>

              <p className="micro-label">GREENBYTE · PROMPT SUSTAINABILITY RECORD</p>
              <h1>{Number(r.net_avoided_g || 0).toFixed(4)} <em>ACU</em></h1>
              <p className="certificate-lead">Estimated net CO₂e avoided relative to the configured cloud AI baseline for this verified inference session.</p>

              <div className="certificate-summary-grid">
                <div><span>Cloud footprint</span><b>{carbon(r.cloud_carbon_g)}</b></div>
                <div><span>Local footprint</span><b>{carbon(r.local_carbon_g)}</b></div>
                <div><span>Reduction</span><b>{Number(r.reduction_pct || 0).toFixed(1)}%</b></div>
                <div><span>Methodology</span><b>{r.methodology_version}</b></div>
              </div>
            </section>

            <section className="certificate-detail-grid">
              <article className="verify-card">
                <p className="micro-label">CERTIFICATE IDENTITY</p>
                <h2>Record details</h2>
                <dl className="detail-list">
                  <div><dt>Certificate ID</dt><dd>{r.certificate_id}</dd></div>
                  <div><dt>Session ID</dt><dd>{r.session_id}</dd></div>
                  <div><dt>Ledger block</dt><dd>#{r.block_index}</dd></div>
                  <div><dt>Verified at</dt><dd>{dt(r.verified_at)}</dd></div>
                </dl>
              </article>

              <article className="verify-card">
                <p className="micro-label">AI WORKLOAD</p>
                <h2>Cloud vs local</h2>
                <dl className="detail-list">
                  <div><dt>Local model</dt><dd>{r.model}</dd></div>
                  <div><dt>Local tokens</dt><dd>{r.input_tokens} input · {r.output_tokens} output</dd></div>
                  <div><dt>Cloud model</dt><dd>{r.cloud_model || 'Configured cloud baseline'}</dd></div>
                  <div><dt>Cloud tokens</dt><dd>{r.cloud_input_tokens ?? '—'} input · {r.cloud_output_tokens ?? '—'} output</dd></div>
                </dl>
              </article>

              <article className="verify-card wide-card">
                <p className="micro-label">PROOF REFERENCE</p>
                <h2>Cryptographic anchor</h2>
                <div className="hash-display"><span>Stored block hash</span><code>{r.proof_hash}</code></div>
                <p className="verify-note">This certificate ID is the human-readable reference. The cryptographic proof is checked separately against the stored evidence hash, methodology hash, block hash and chain linkage.</p>
              </article>
            </section>

            <div className="verification-actions">
              <a href={`/proof/${encodeURIComponent(r.certificate_id)}`} className="verify-button secondary">View proof evidence</a>
              <a href={`/verify/${encodeURIComponent(r.certificate_id)}`} className="verify-button primary">Verify integrity →</a>
              <button onClick={copyLink} className="verify-button ghost">{copied ? 'Link copied ✓' : 'Copy certificate link'}</button>
              <button onClick={() => window.print()} className="verify-button ghost">Print / Save PDF</button>
            </div>

            <p className="verification-disclaimer">GreenByte ACU is an internal avoided-carbon accounting unit for this proof-of-concept. It is not a regulated carbon credit, offset, financial instrument or government-issued certificate.</p>
          </>
        )}
      </div>
    </main>
  );
}
