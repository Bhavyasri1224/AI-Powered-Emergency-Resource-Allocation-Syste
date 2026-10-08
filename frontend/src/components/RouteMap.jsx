import { useEffect } from 'react';
import L from 'leaflet';
import { MapContainer, Marker, Polyline, TileLayer, Tooltip, useMap } from 'react-leaflet';

const emergencyIcon = L.divIcon({ className: 'map-pin map-pin-emergency', html: '<span></span>', iconSize: [22, 22], iconAnchor: [11, 11] });
const recommendedIcon = L.divIcon({ className: 'map-pin map-pin-hospital', html: '<span></span>', iconSize: [22, 22], iconAnchor: [11, 11] });
const alternativeIcon = L.divIcon({ className: 'map-pin map-pin-alt', html: '<span></span>', iconSize: [15, 15], iconAnchor: [7.5, 7.5] });

function FitRoute({ positions }) {
  const map = useMap();
  useEffect(() => {
    if (positions.length > 1) map.fitBounds(positions, { padding: [36, 36], maxZoom: 14 });
  }, [map, positions]);
  return null;
}

export default function RouteMap({ response, incident }) {
  const recommended = response?.recommended_hospital;
  const route = response?.route;
  const center = [incident.latitude, incident.longitude];
  const routePositions = route?.geometry || [];
  const markers = [recommended, ...(response?.alternative_hospitals || [])].filter(Boolean);

  return (
    <div className="map-frame">
      <MapContainer center={center} zoom={12} scrollWheelZoom={false}>
        <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <Marker position={center} icon={emergencyIcon}><Tooltip>Emergency location</Tooltip></Marker>
        {markers.map((hospital, index) => <Marker key={hospital.name} position={[hospital.latitude, hospital.longitude]} icon={index === 0 ? recommendedIcon : alternativeIcon}><Tooltip>{index === 0 ? 'Recommended: ' : 'Alternative: '}{hospital.name}</Tooltip></Marker>)}
        {routePositions.length > 1 && <><Polyline positions={routePositions} pathOptions={{ color: '#087f8c', weight: 5, opacity: 0.88 }} /><FitRoute positions={routePositions} /></>}
      </MapContainer>
      {!response && <div className="map-empty"><MapPin size={18} /><span>Submit an incident to plot the recommended route</span></div>}
      <div className="map-legend"><span><i className="legend-emergency" />Incident</span><span><i className="legend-hospital" />Recommended</span><span><i className="legend-alt" />Alternatives</span></div>
    </div>
  );
}
