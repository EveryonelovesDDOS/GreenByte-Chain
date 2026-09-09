import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

const API_BASE = process.env.NEXT_PUBLIC_GREENBYTE_API || 'http://127.0.0.1:5000';

function Flag({ ok, children }: { ok: boolean; children: React.ReactNode }) {
  return <span className={ok ? 'check-chip good-check' : 'check-chip bad-check'}>{ok ? '✓' : '×'} {children}</span>;
}

function HashBox({ label, value }: { label: string; value?: string }) {
  return <div className="hash-box"><span>{label}</span><code>{value || '—'}</code></div>;
}

export default function ProofPage() {
  const router = useRouter();
  const id = typeof router.query.id === 'string' ? router.query.id : '';
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    fetch(`${API_BASE}/api/proof/${encodeURIComponent(id)}`, { cache: 'no-store' })
      .then(async (r) => {
        const body = await r.json();
        if (!r.ok) throw new Error(body.error || `HTTP ${r.status}`);
        return body;
      })
      .then(setData)
      .catch((e) => setError(e.message || 'Unable to load proof'));
  }, [id]);

  const record = data?.record;
  const block = data?.ledger?.block;

  return (
    <main className="verification-page proof-page">
      <div className="verification-glow" />
      <div className="verification-shell">
        <header className="verify-topbar">
          <a href="/" className="verify-brand"><span>◒</span><b>GreenByte</b><small>Evidence Explorer</small></a>
          <a href="/" className="back-dashboard">← Back to dashboard</a>
        </header>

        {!data && !error && <div className="verify-loading">Reading proof evidence from the ledger…</div>}
        {error && <div className="verify-error"><b>Proof unavailable</b><span>{error}</span></div>}

        {data && (
          <>
            <section className="proof-hero">
              <p className="micro-label">PROOF OF EVIDENCE</p>
              <h1>Cryptographic record <em>#{record.block_index}</em></h1>
              <p>Evidence for <b>{record.certificate_id}</b> is reconstructed from the stored session and compared with the hashes committed to the GreenByte ledger.</p>
              <div className="check-row">
                <Flag ok={!!data.evidence?.valid}>Evidence hash</Flag>
                <Flag ok={!!data.methodology?.valid}>Methodology hash</Flag>
                <Flag ok={!!data.ledger?.block_check?.hash_valid}>Block hash</Flag>
                <Flag ok={!!data.ledger?.chain_valid}>Chain integrity</Flag>
              </div>
            </section>

            <section className="proof-grid">
              <article className="verify-card wide-card">
                <p className="micro-label">EVIDENCE FINGERPRINT</p>
                <h2>Evidence hash</h2>
                <HashBox label="Stored in ledger" value={data.evidence?.stored_hash} />
                <HashBox label="Recalculated now" value={data.evidence?.recalculated_hash} />
              </article>

              <article className="verify-card wide-card">
                <p className="micro-label">METHODOLOGY FINGERPRINT</p>
                <h2>Methodology hash</h2>
                <HashBox label="Stored in ledger" value={data.methodology?.stored_hash} />
                <HashBox label="Recalculated now" value={data.methodology?.recalculated_hash} />
              </article>

              <article className="verify-card">
                <p className="micro-label">BLOCK LINKAGE</p>
                <h2>Ledger anchor</h2>
                <HashBox label="Block hash" value={block?.block_hash} />
                <HashBox label="Previous block hash" value={block?.previous_hash} />
                <div className="mini-stat"><span>Block</span><b>#{block?.block_index}</b></div>
              </article>

              <article className="verify-card">
                <p className="micro-label">SESSION EVIDENCE</p>
                <h2>Stored values</h2>
                <dl className="detail-list">
                  <div><dt>Local model</dt><dd>{record.model}</dd></div>
                  <div><dt>Cloud model</dt><dd>{record.cloud_model}</dd></div>
                  <div><dt>Local energy</dt><dd>{Number(record.local_energy_j || 0).toFixed(4)} J</dd></div>
                  <div><dt>Net avoided</dt><dd>{Number(record.net_avoided_g || 0).toFixed(4)} ACU</dd></div>
                </dl>
              </article>
            </section>

            <section className="raw-evidence-card">
              <div><p className="micro-label">RAW EVIDENCE</p><h2>Canonical evidence payload</h2></div>
              <pre>{JSON.stringify(data.evidence?.payload || {}, null, 2)}</pre>
            </section>

            <div className="verification-actions">
              <a href={`/certificate/${encodeURIComponent(record.certificate_id)}`} className="verify-button secondary">Open certificate</a>
              <a href={`/verify/${encodeURIComponent(record.certificate_id)}`} className="verify-button primary">Run verification →</a>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
