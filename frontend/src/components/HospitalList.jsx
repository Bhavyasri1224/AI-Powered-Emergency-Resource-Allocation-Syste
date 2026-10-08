import { Activity, BedDouble, HeartPulse, MapPin, Users } from 'lucide-react';

export default function HospitalList({ hospital, rank, isRecommended = false }) {
  return (
    <article className={`hospital-row ${isRecommended ? 'recommended-row' : ''}`}>
      <div className="hospital-rank">{String(rank).padStart(2, '0')}</div>
      <div className="hospital-main">
        <div className="hospital-title"><h3>{hospital.name}</h3><span className="score-pill">{hospital.score.toFixed(1)} <small>score</small></span></div>
        <p className="hospital-reasons">{hospital.reasons.join(' · ')}</p>
        <div className="hospital-stats">
          <span><MapPin size={12} />{hospital.distance_km} km</span>
          <span><HeartPulse size={12} />{hospital.icu_beds} ICU</span>
          <span><BedDouble size={12} />{hospital.available_beds} beds</span>
          <span><Users size={12} />{hospital.current_patient_load}% load</span>
          {hospital.icu_available && <span className="support-indicator"><Activity size={12} /> Critical care</span>}
        </div>
      </div>
    </article>
  );
}
