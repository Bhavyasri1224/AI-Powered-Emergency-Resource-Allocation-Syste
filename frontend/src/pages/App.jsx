import { useEffect, useState } from 'react';
import { Activity, AlertCircle, ArrowDownRight, ArrowUpRight, BadgeCheck, Clock3, HeartPulse, MapPin, Radio, ShieldAlert, Siren } from 'lucide-react';
import EmergencyForm from '../components/EmergencyForm.jsx';
import HospitalList from '../components/HospitalList.jsx';
import RouteMap from '../components/RouteMap.jsx';
import { getHealth, submitEmergency } from '../services/api.js';

const emptyIncident = { latitude: 40.7128, longitude: -74.006 };

export default function App() {
  const [response, setResponse] = useState(null);
  const [incident, setIncident] = useState(emptyIncident);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [apiOnline, setApiOnline] = useState(false);

  useEffect(() => { getHealth().then(() => setApiOnline(true)).catch(() => setApiOnline(false)); }, []);

  async function assess(payload) {
    setLoading(true);
    setError('');
    setIncident({ latitude: payload.latitude, longitude: payload.longitude });
    try {
      const result = await submitEmergency(payload);
      setResponse(result);
    } catch (failure) {
      setError(`${failure.message}. Confirm the API is running at localhost:8000.`);
      setResponse(null);
    } finally {
      setLoading(false);
    }
  }

  const severity = response?.severity?.toLowerCase();
  const SeverityIcon = severity === 'critical' ? Siren : severity === 'high' ? AlertCircle : BadgeCheck;
  const scoreFactors = response?.recommended_hospital?.score_breakdown;
  const topFactors = scoreFactors ? Object.entries(scoreFactors).sort((a, b) => b[1] - a[1]).slice(0, 3) : [];

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="Relay dashboard home"><span className="brand-mark"><Activity size={19} /></span><span>relay<span className="brand-dot">.</span></span></a>
        <div className="topbar-meta"><span className="sample-badge"><span /> Simulated data</span><span className={`api-status ${apiOnline ? 'is-online' : ''}`}><i />{apiOnline ? 'API connected' : 'API unavailable'}</span><span className="ops-label">OPERATIONS DESK <b>·</b> 01</span></div>
      </header>
      <main id="top">
        <div className="page-intro"><div><span className="eyebrow">EMERGENCY RESPONSE / RESOURCE ALLOCATION</span><h1>Incident coordination</h1><p>Assess severity. Match care capability. Dispatch with clarity.</p></div><div className="desk-time"><span>LOCAL DESK TIME</span><strong>{new Intl.DateTimeFormat('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }).format(new Date())}</strong><small>Sample city · UTC−04</small></div></div>
        <div className="workspace-grid">
          <aside className="intake-column"><EmergencyForm onSubmit={assess} loading={loading} /></aside>
          <section className="results-column" aria-live="polite">
            {error && <div className="error-banner"><AlertCircle size={17} /><div><strong>Unable to complete assessment</strong><span>{error}</span></div></div>}
            <div className="section-kicker"><span>RESPONSE OVERVIEW</span><span className="section-line" />{response && <span className="event-id">EVENT RLY-{new Date().getTime().toString().slice(-5)}</span>}</div>
            {response ? <>
              <div className="overview-strip">
                <article className={`severity-panel severity-${severity}`}>
                  <div className="severity-head"><span><SeverityIcon size={17} /> TRIAGE RISK ESTIMATE</span><i className="pulse-dot" /></div>
                  <strong className="severity-value">{response.severity}</strong>
                  <div className="confidence-line"><span>Model confidence</span><strong>{Math.round(response.confidence * 100)}%</strong></div>
                  <div className="confidence-track"><i style={{ width: `${response.confidence * 100}%` }} /></div>
                </article>
                <article className="travel-panel">
                  <div className="travel-icon"><Clock3 size={17} /></div><span className="eyebrow">EST. TRAVEL TIME</span>
                  <strong>{response.estimated_travel_time || 'Unavailable'}</strong>
                  <span className="travel-distance">{response.route?.distance_km ?? '--'} km · {response.route?.label ?? 'Route unavailable'}</span>
                </article>
              </div>
              <section className="result-section hospital-section">
                <div className="section-title-row"><div><span className="eyebrow">CARE DESTINATION</span><h2>Recommended hospital</h2></div><span className="recommendation-tag"><HeartPulse size={13} /> BEST MATCH</span></div>
                {response.recommended_hospital ? <>
                  <HospitalList hospital={response.recommended_hospital} rank={1} isRecommended />
                  <div className="match-reasons"><div className="reason-header"><span>Why this match</span><strong>Weighted score · {response.recommended_hospital.score}/100</strong></div><div className="factor-grid">{topFactors.map(([factor, value]) => <span key={factor}><ArrowUpRight size={13} />{factor.replaceAll('_', ' ')} <b>{Math.round(value)}%</b></span>)}</div></div>
                </> : <div className="no-match">{response.message || 'No suitable hospital found. Trained dispatch personnel should select an alternative.'}</div>}
              </section>
              <section className="result-section route-section">
                <div className="section-title-row"><div><span className="eyebrow">AMBULANCE ROUTE</span><h2>Dispatch map</h2></div>{response.route && <span className={`route-source ${response.route.source}`}><span />{response.route.label}</span>}</div>
                <RouteMap response={response} incident={incident} />
                <div className="route-meta"><span><MapPin size={13} />{response.route?.distance_km ?? '--'} km estimated distance</span><span><Clock3 size={13} />{response.estimated_travel_time || 'Time unavailable'}</span><span className="traffic-note">Traffic: {response.route?.traffic || 'not available'}</span></div>
              </section>
              <section className="result-section alternatives-section">
                <div className="section-title-row"><div><span className="eyebrow">RANKED ALTERNATIVES</span><h2>Other suitable hospitals</h2></div><span className="muted-count">{response.alternative_hospitals.length} OPTIONS</span></div>
                {response.alternative_hospitals.length ? response.alternative_hospitals.map((hospital, index) => <HospitalList key={hospital.name} hospital={hospital} rank={index + 2} />) : <p className="muted-copy">No additional suitable hospitals in this sample dataset.</p>}
              </section>
              <section className="result-section explain-section">
                <div className="section-title-row"><div><span className="eyebrow">DECISION CONTEXT</span><h2>Recommendation rationale</h2></div></div>
                <div className="explain-grid"><div><h3><ShieldAlert size={15} /> Why this severity?</h3><ul>{response.severity_reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul></div><div><h3><HeartPulse size={15} /> Why this hospital?</h3><ul>{(response.recommended_hospital?.reasons || ['No hospital recommendation available']).map((reason) => <li key={reason}>{reason}</li>)}</ul></div></div>
              </section>
            </> : <>
              <div className="empty-state"><div className="empty-symbol"><Radio size={24} /></div><span className="eyebrow">AWAITING INCIDENT</span><h2>Response recommendations<br />will appear here</h2><p>Enter incident details, or use the demo scenario to see severity, hospital matching and a route in one assessment.</p><div className="empty-steps"><span><i>01</i> Triage estimate</span><ArrowDownRight size={14} /><span><i>02</i> Capability match</span><ArrowDownRight size={14} /><span><i>03</i> Route estimate</span></div></div>
              <div className="preview-grid"><div><span className="eyebrow">HOSPITAL NETWORK</span><strong>10</strong><small>sample facilities</small></div><div><span className="eyebrow">ROUTING</span><strong>OSRM</strong><small>with local fallback</small></div></div>
            </>}
          </section>
        </div>
      </main>
      <footer className="disclaimer-bar"><ShieldAlert size={15} /><span><strong>Decision-support only.</strong> Final medical and emergency decisions are made by trained personnel.</span><span className="footer-data">All hospital and emergency data is simulated/sample data.</span></footer>
    </div>
  );
}
