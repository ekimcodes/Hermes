import React from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

const GridMap = ({ predictions }) => {
    // Center map to cover SF, Oakland, and Berkeley
    const defaultCenter = [37.82, -122.35];

    const getColor = (prob) => {
        if (prob > 0.7) return 'red';
        if (prob > 0.5) return 'orange';
        if (prob > 0.3) return 'yellow';
        return 'green';
    };

    return (
        <div className="h-full w-full rounded-none shadow-none z-0">
            <MapContainer center={defaultCenter} zoom={11} style={{ height: '100%', width: '100%' }}>
                <TileLayer
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                {predictions.map((pred) => {
                    // Mock random location spread across the Bay Area for demo
                    // Spread increased to 0.25 to cover SF and East Bay
                    // Deterministic pseudo-random based on feeder ID would be better, but staying simple
                    const seed = parseInt(pred.feeder_id.replace("F-", ""));

                    // Simple Pseudo-random matching Python's random.seed(seed)
                    // Note: This won't perfectly match Python's Mersenne Twister but provides consistent locations
                    const pseudoRandom = (input) => {
                        let t = input += 0x6D2B79F5;
                        t = Math.imul(t ^ t >>> 15, t | 1);
                        t ^= t + Math.imul(t ^ t >>> 7, t | 61);
                        return ((t ^ t >>> 14) >>> 0) / 4294967296;
                    }

                    const r1 = pseudoRandom(seed);
                    const r2 = pseudoRandom(seed + 1);

                    const lat = defaultCenter[0] + (r1 - 0.5) * 0.25;
                    const lng = defaultCenter[1] + (r2 - 0.5) * 0.35;

                    return (
                        <CircleMarker
                            key={pred.feeder_id}
                            center={[lat, lng]}
                            radius={8}
                            color={getColor(pred.outage_probability)}
                            fillColor={getColor(pred.outage_probability)}
                            fillOpacity={0.7}
                        >
                            <Popup>
                                <div className="p-1">
                                    <h3 className="font-bold text-lg mb-1">{pred.feeder_id}</h3>
                                    <div className="text-sm space-y-1">
                                        <p>Risk Score: <span className="font-semibold">{(pred.outage_probability * 100).toFixed(1)}%</span></p>
                                        <div className="flex items-center space-x-2 bg-blue-50 p-1 rounded">
                                            <span>💨 Wind:</span>
                                            <span className="font-bold text-blue-800">{pred.wind_speed ? pred.wind_speed.toFixed(1) : '-'} mph</span>
                                        </div>
                                        <p>Status: <span className="uppercase font-medium">{pred.severity}</span></p>
                                        <p>Est. Restoration: <span className="font-medium">{pred.etr_minutes ? Math.round(pred.etr_minutes) + ' min' : 'N/A'}</span></p>
                                    </div>
                                </div>
                            </Popup>
                        </CircleMarker>
                    );
                })}
            </MapContainer>
        </div>
    );
};

export default GridMap;
