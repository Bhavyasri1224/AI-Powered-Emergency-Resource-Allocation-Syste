# AI-Powered Emergency Resource Allocation System

A local, hackathon-ready decision-support prototype that estimates triage-style severity, ranks suitable facilities by capability and capacity, and estimates an ambulance route. This is a prototype, not a dispatch or clinical system.

> **Decision-support only. Final medical and emergency decisions are made by trained personnel.**

All hospital and emergency records in this project are **simulated/sample data**. The ML dataset is synthetic and rule-generated with a small amount of label noise. The app does not consume government or live hospital data. Traffic is not available; travel time uses the route provider's estimate when available or a distance/average-speed estimate for the simulated fallback.

## Requirements

- Python 3.10 or newer (standard CPython recommended)
- Node.js 18 or newer and npm
- Internet access is needed only for installing packages, OpenStreetMap tiles, and the optional public OSRM routing request

## Run locally

From the project root, install backend packages and train the model once:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python ml/train.py
```

Install the frontend packages:

```powershell
cd frontend
npm install
cd ..
```

Open two terminals from the project root and start each service:

```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

```powershell
cd frontend
npm run dev
```

Open <http://localhost:5173>. FastAPI docs are at <http://localhost:8000/docs>. SQLite initializes and seeds itself from `backend/data/hospitals.csv` on first backend start. The trained model lives at `ml/model.pkl`; metrics are written to `ml/metrics.json`.

## Demo script

1. Start the backend and frontend, then open the dashboard.
2. Click **Demo emergency**. It fills a Road Accident with two patients, unconsciousness, severe bleeding, a fracture, and the sample city coordinates.
3. Click **Assess & find resources**. The dashboard shows a triage-style severity estimate and probability confidence, top-ranked suitable facilities with score reasons, a mapped route, estimated distance and travel time, and alternatives.
4. Change the emergency type to Heart Emergency or Stroke and select the relevant symptom. Submit again to see specialization-sensitive ranking and a changed risk estimate.
5. To check route fallback, run the backend without external network access; the response should be labeled **Simulated route** and show the traffic-unavailable estimate. If the API is stopped, the frontend displays an actionable connection error.

## API overview

All request bodies are validated with Pydantic. Local frontend CORS is enabled for port 5173.

- `GET /health` reports API status and the sample-data status.
- `GET /hospitals` returns the seeded sample facilities.
- `POST /predict-severity` accepts emergency details and returns severity, probability confidence, plain-language reasons, and the disclaimer.
- `POST /recommend-hospital` returns up to three hospitals with suitability scores and score breakdown.
- `POST /calculate-route` accepts origin/destination latitude and longitude, tries the public OSRM route service, then falls back to an explicitly labeled simulated route.
- `POST /emergency-response` orchestrates prediction, ranking, and route calculation for the complete workflow.

Example response fields include `severity`, `confidence`, `severity_reasons`, `recommended_hospital`, `alternative_hospitals`, `route.geometry` (latitude/longitude pairs), `route.source`, `estimated_travel_time`, `data_label`, and `disclaimer`.

## Synthetic severity model

`ml/train.py` generates 1,800 synthetic rows (600 per severity label) using documented rule features for emergency type, age, patient count, and injury/symptom indicators. Severe symptoms contribute risk points; heart/stroke event types, multiple patients, and age extremes add weight; a low-risk stable report reduces risk. Thresholds assign Medium, High, or Critical, followed by 3.5% adjacent-class label perturbation. This is generated training data, not clinical evidence.

The script stratifies its train/test split, compares Random Forest and Logistic Regression, prints accuracy, macro precision/recall/F1 and confusion matrices, and saves the higher macro-F1 pipeline. Retrain with:

```powershell
python ml/train.py
```

To run a sample inference:

```powershell
python ml/predict.py
```

The probability is model confidence on this synthetic task, not calibrated medical certainty or a diagnosis. Plain-language reasons are based on selected symptoms, event type, and patient count rather than causal medical explanations.

## Hospital ranking

Hospitals are simulated in a sample-city area and seeded into SQLite from `backend/data/hospitals.csv`. SQLite is isolated behind `backend/database/db.py`, keeping a small repository boundary for a later PostgreSQL adapter.

Each factor is min-max normalized to 0-1 among eligible hospitals; score is the weighted sum multiplied by 100. The weight configuration is centralized in `backend/services/ranking.py`:

| Factor | Critical | High | Medium |
| --- | ---: | ---: | ---: |
| Distance (closer) | 0.12 | 0.20 | 0.30 |
| ICU availability | 0.28 | 0.20 | 0.08 |
| Bed availability | 0.12 | 0.17 | 0.20 |
| Specialization match | 0.23 | 0.18 | 0.14 |
| Lower current patient load | 0.10 | 0.12 | 0.15 |
| Emergency support | 0.15 | 0.13 | 0.13 |

Critical cases exclude facilities with no ICU beds; all severity levels exclude facilities without enough available beds for the reported patient count. If none remain, the API returns a clear no-suitable-hospital message. The distance factor uses haversine straight-line distance for ranking, not road distance.

## Routing and map

The browser map uses Leaflet with OpenStreetMap tiles. A public OSRM route is attempted with a short timeout; connection, response, and route-data failures use a curved coordinate interpolation marked **Simulated route**. Fallback route distance applies a 1.28 detour factor to haversine distance and estimates duration at 28 km/h. No live traffic source is used, so the interface states: **Traffic: not available (estimate based on distance/average speed)**. Public tile and routing services have their own availability and usage policies.

## Tests and build

```powershell
python -m pytest backend/tests -q
cd frontend
npm run build
```

## Limitations and next steps

- Synthetic labels and generated facility capacities are not clinically validated and must not guide real care or dispatch.
- Availability and patient load are fixed sample values; there are no live hospital, ambulance, or emergency feeds.
- OSRM and OSM are public services; route availability and coverage are not guaranteed. Fallback geometry is illustrative, not a navigable road route.
- No live traffic, authentication, audit logging, persistence of emergency incidents, or production deployment controls are included.
- Future work: approved and clinically reviewed training data, live hospital capacity feeds, ambulance/traffic data, calibration and external model validation, PostgreSQL, access control and audit history, and operational safety review.
