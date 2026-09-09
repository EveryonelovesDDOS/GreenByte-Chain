import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

const API_BASE = process.env.NEXT_PUBLIC_GREENBYTE_API || 'http://127.0.0.1:5000';

function Check({ label, ok, detail }: { label: string; ok: boolean; detail: string }) {
  return (
    <div className={`integrity-check ${ok ? 'pass' : 'fail'}`}>
      <span className="integrity-icon">{ok ? '✓' : '×'}</span>
      <div><b>{label}</b><small>{detail}</small></div>
      <em>{ok ? 'PASS' : 'FAIL'}</em>
    </div>
  );
}

export default function VerifyPage() {
  const router = useRouter();
  const id = typeof router.query.id === 'string' ? router.query.id : '';
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!id) return;
    fetch(`${API_BASE}/api/verify/${encodeURIComponent(id)}`, { cache: 'no-store' })
      .then(async (r) => {
        const body = await r.json();
        if (!r.ok) throw new Error(body.error || `HTTP ${r.status}`);
        return body;
      })
      .then(setData)
      .catch((e) => setError(e.message || 'Unable to verify certificate'));
  }, [id]);

  const r = data?.record;
  const blockCheck = data?.ledger?.block_check || {};

  return (
    <main className="verification-page verify-result-page">
      <div className="verification-glow" />
      <div className="verification-shell narrow-shell">
        <header className="verify-topbar">
          <a href="/" className="verify-brand"><span>◒</span><b>GreenByte</b><small>Integrity Verification</small></a>
          <a href="/" className="back-dashboard">← Back to dashboard</a>
        </header>

        {!data && !error && <div className="verify-loading">Recalculating evidence and checking ledger integrity…</div>}
        {error && <div className="verify-error"><b>Verification unavailable</b><span>{error}</span></div>}

        {data && (
          <>
            <section className={`verification-result ${data.verified ? 'valid-result' : 'invalid-result'}`}>
              <span className="result-icon">{data.verified ? '✓' : '×'}</span>
              <p className="micro-label">GREENBYTE INTEGRITY CHECK</p>
              <h1>{data.verified ? 'VERIFIED' : 'INVALID'}</h1>
              <p>{data.verified ? 'The stored evidence, methodology fingerprint, block hash and ledger linkage all match.' : 'One or more cryptographic integrity checks did not match the stored record.'}</p>
              <div className="verified-id"><span>Certificate</span><b>{data.certificate_id}</b></div>
            </section>

            <section className="integrity-list">
              <Check label="Evidence hash" ok={!!data.evidence?.valid} detail="Recalculated session evidence matches the hash stored in the ledger." />
              <Check label="Methodology hash" ok={!!data.methodology?.valid} detail="Current reconstruction matches the methodology fingerprint committed for this record." />
              <Check label="Block hash" ok={!!blockCheck.hash_valid} detail="Stored block contents reproduce the committed SHA-256 block hash." />
              <Check label="Previous block link" ok={!!blockCheck.previous_link_valid} detail="This block points to the exact hash of the preceding GreenByte ledger block." />
              <Check label="Session-to-block binding" ok={!!data.ledger?.block_payload_matches_session} detail="The ledger payload is bound to the same session and source identity." />
              <Check label="Full chain integrity" ok={!!data.ledger?.chain_valid} detail={`GreenByte ledger verified through block #${data.ledger?.height ?? '—'}.`} />
            </section>

            {r && (
              <section className="verification-record-strip">
                <div><span>ACU</span><b>{Number(r.net_avoided_g || 0).toFixed(4)}</b></div>
                <div><span>Cloud CO₂e</span><b>{Number(r.cloud_carbon_g || 0).toFixed(4)} g</b></div>
                <div><span>Local CO₂e</span><b>{Number(r.local_carbon_g || 0) > 0 && Number(r.local_carbon_g) < .0001 ? '<0.0001 g' : `${Number(r.local_carbon_g || 0).toFixed(4)} g`}</b></div>
                <div><span>Block</span><b>#{r.block_index}</b></div>
              </section>
            )}

            <div className="verification-actions centered-actions">
              <a href={`/certificate/${encodeURIComponent(data.certificate_id)}`} className="verify-button secondary">View certificate</a>
              <a href={`/proof/${encodeURIComponent(data.certificate_id)}`} className="verify-button primary">Inspect proof evidence →</a>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
