import { useState } from 'react';
import { Clock3, MapPin, Send, Sparkles } from 'lucide-react';

const initialForm = {
  emergency_type: 'Road Accident',
  age: 34,
  patient_count: 1,
  unconscious: false,
  severe_bleeding: false,
  difficulty_breathing: false,
  chest_pain: false,
  stroke_signs: false,
  burns: false,
  fracture: false,
  conscious_stable: false,
  latitude: 40.7128,
  longitude: -74.006,
  emergency_time: new Date().toISOString().slice(0, 16),
  notes: '',
};

const indicators = [
  ['unconscious', 'Unconscious'],
  ['severe_bleeding', 'Severe bleeding'],
  ['difficulty_breathing', 'Difficulty breathing'],
  ['chest_pain', 'Chest pain'],
  ['stroke_signs', 'Stroke signs'],
  ['burns', 'Burns'],
  ['fracture', 'Possible fracture'],
  ['conscious_stable', 'Conscious and stable'],
];

export default function EmergencyForm({ onSubmit, loading }) {
  const [form, setForm] = useState(initialForm);
  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));

  function loadDemo() {
    setForm({
      ...initialForm,
      emergency_type: 'Road Accident',
      age: 34,
      patient_count: 2,
      unconscious: true,
      severe_bleeding: true,
      fracture: true,
      latitude: 40.7128,
      longitude: -74.006,
      emergency_time: new Date().toISOString().slice(0, 16),
      notes: 'Two patients from a road collision. One reported unconscious with severe bleeding.',
    });
  }

  function submit(event) {
    event.preventDefault();
    const payload = {
      ...form,
      age: Number(form.age),
      patient_count: Number(form.patient_count),
      latitude: Number(form.latitude),
      longitude: Number(form.longitude),
      emergency_time: form.emergency_time ? new Date(form.emergency_time).toISOString() : null,
    };
    onSubmit(payload);
  }

  return (
    <form className="intake-form" onSubmit={submit}>
      <div className="form-heading">
        <div><span className="eyebrow">NEW INCIDENT</span><h2>Emergency details</h2></div>
        <button type="button" className="demo-button" onClick={loadDemo}><Sparkles size={15} /> Demo emergency</button>
      </div>
      <div className="field-grid">
        <label className="field"><span>Emergency type</span>
          <select value={form.emergency_type} onChange={(event) => update('emergency_type', event.target.value)}>
            {['Road Accident', 'Heart Emergency', 'Stroke', 'Fire/Disaster', 'Other'].map((type) => <option key={type}>{type}</option>)}
          </select>
        </label>
        <label className="field"><span>Patient age</span><input type="number" min="0" max="120" required value={form.age} onChange={(event) => update('age', event.target.value)} /></label>
        <label className="field"><span>Number of patients</span><input type="number" min="1" max="100" required value={form.patient_count} onChange={(event) => update('patient_count', event.target.value)} /></label>
        <label className="field"><span><Clock3 size={13} /> Time of emergency</span><input type="datetime-local" value={form.emergency_time} onChange={(event) => update('emergency_time', event.target.value)} /></label>
      </div>
      <fieldset className="symptom-fieldset">
        <legend>Symptoms and injury indicators</legend>
        <div className="symptom-grid">{indicators.map(([key, label]) => (
          <label className="check-row" key={key}><input type="checkbox" checked={form[key]} onChange={(event) => update(key, event.target.checked)} /><span>{label}</span></label>
        ))}</div>
      </fieldset>
      <div className="location-title"><span><MapPin size={14} /> Emergency location</span><small>Sample city coordinates</small></div>
      <div className="field-grid coordinate-grid">
        <label className="field"><span>Latitude</span><input type="number" min="-90" max="90" step="any" required value={form.latitude} onChange={(event) => update('latitude', event.target.value)} /></label>
        <label className="field"><span>Longitude</span><input type="number" min="-180" max="180" step="any" required value={form.longitude} onChange={(event) => update('longitude', event.target.value)} /></label>
      </div>
      <label className="field notes-field"><span>Additional notes <small>Optional</small></span><textarea maxLength="1000" rows="2" placeholder="Relevant context for dispatch..." value={form.notes} onChange={(event) => update('notes', event.target.value)} /></label>
      <button className="submit-button" type="submit" disabled={loading}><Send size={16} />{loading ? 'Assessing incident...' : 'Assess & find resources'}</button>
      <p className="form-footnote">Severity is a triage-style risk estimate, not a medical diagnosis.</p>
    </form>
  );
}
