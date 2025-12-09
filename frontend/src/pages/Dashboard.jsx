import React, { useEffect, useState } from 'react';
import GridMap from '../components/Map/GridMap';
import RiskSummary from '../components/Widgets/RiskSummary';
import { predictOutages, getHealth } from '../services/api';

const Dashboard = () => {
    const [predictions, setPredictions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [systemStatus, setSystemStatus] = useState('Checking...');
    const [stormMode, setStormMode] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const health = await getHealth();
                setSystemStatus(health.status);

                // Generate 200 feeders programmatically
                const feederIds = Array.from({ length: 200 }, (_, i) => `F-${1000 + i}`);

                // If Storm Mode is on, override weather
                const weatherOverride = stormMode ? { wind_speed: 80, temperature: 105 } : null;

                // We need to update predictOutages to accept the override
                // Since api.js might need update, we pass it here assuming we update api.js next
                const data = await predictOutages(feederIds, weatherOverride);

                setPredictions(data.predictions || []);
            } catch (error) {
                console.error("Failed to fetch dashboard data:", error);
                setSystemStatus('Error');
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 10000); // Poll every 10s for faster updates
        return () => clearInterval(interval);
    }, [stormMode]); // Re-run when stormMode changes

    return (
        <div className="flex flex-col h-screen bg-gray-50 overflow-hidden">
            {/* Header - Fixed Height */}
            <header className="flex-none bg-white shadow-sm z-10 p-4 flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Grid Outage Prediction</h1>
                    <p className="text-sm text-gray-600">Restoration Time Estimator</p>
                </div>
                <div className="flex items-center space-x-4">
                    <button
                        onClick={() => setStormMode(!stormMode)}
                        className={`px-4 py-2 rounded font-bold text-white transition-colors ${stormMode ? 'bg-red-600 hover:bg-red-700' : 'bg-blue-500 hover:bg-blue-600'
                            }`}
                    >
                        {stormMode ? 'STOP SIMULATION' : 'SIMULATE STORM'}
                    </button>
                    <div className="flex items-center space-x-2">
                        <span className={`h-3 w-3 rounded-full ${systemStatus === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`}></span>
                        <span className="text-sm font-medium">{systemStatus === 'healthy' ? 'System Online' : 'System Offline'}</span>
                    </div>
                </div>
            </header>

            {/* Main Content - Flex Grow */}
            <div className="flex-1 flex overflow-hidden">
                {loading ? (
                    <div className="w-full flex justify-center items-center">
                        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                    </div>
                ) : (
                    <>
                        {/* Left Sidebar - Scrollable */}
                        <div className="w-1/3 min-w-[300px] max-w-[400px] flex flex-col border-r border-gray-200 bg-white">
                            <div className="p-4 flex-none">
                                <RiskSummary predictions={predictions} />
                            </div>

                            <div className="flex-1 overflow-y-auto p-4 pt-0">
                                <h3 className="font-bold mb-2 text-lg sticky top-0 bg-white py-2 border-b">Feeder Details</h3>
                                <div className="space-y-2">
                                    {predictions.length === 0 ? (
                                        <p className="text-gray-500 text-center py-4">No data available.</p>
                                    ) : (
                                        predictions.map(p => (
                                            <div key={p.feeder_id} className="border rounded p-3 hover:bg-gray-50 transition-colors">
                                                <div className="flex justify-between items-center mb-1">
                                                    <span className="font-semibold text-gray-700">{p.feeder_id}</span>
                                                    <span className={`text-xs font-bold px-2 py-1 rounded uppercase ${p.severity === 'critical' ? 'bg-red-100 text-red-800' :
                                                        p.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                                                            p.severity === 'moderate' ? 'bg-yellow-100 text-yellow-800' :
                                                                'bg-green-100 text-green-800'
                                                        }`}>{p.severity}</span>
                                                </div>
                                                <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
                                                    <div>
                                                        <span className="block text-xs text-gray-400">Probability</span>
                                                        <span className="font-medium">{(p.outage_probability * 100).toFixed(1)}%</span>
                                                    </div>
                                                    <div>
                                                        <span className="block text-xs text-gray-400">Est. Restoration</span>
                                                        <span className="font-medium">{p.etr_minutes ? Math.round(p.etr_minutes) + ' min' : '-'}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        ))
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Right Map Area - Flexible */}
                        <div className="flex-1 relative bg-gray-200">
                            {/* Pass className to GridMap to ensure it fills height */}
                            <div className="absolute inset-0">
                                <GridMap predictions={predictions} />
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default Dashboard;
