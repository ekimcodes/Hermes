import React from 'react';

const RiskSummary = ({ predictions }) => {
    const totalFeeders = predictions.length;
    const highRisk = predictions.filter(p => p.outage_probability > 0.5).length;
    const criticalRisk = predictions.filter(p => p.severity === 'critical').length;

    return (
        <div className="bg-white p-4 rounded shadow-md mb-4">
            <h2 className="text-xl font-bold mb-2">Grid Risk Summary</h2>
            <div className="grid grid-cols-3 gap-4 text-center">
                <div className="p-2 bg-gray-100 rounded">
                    <p className="text-sm text-gray-600">Total Feeders</p>
                    <p className="text-2xl font-bold">{totalFeeders}</p>
                </div>
                <div className="p-2 bg-yellow-100 rounded">
                    <p className="text-sm text-yellow-800">High Risk</p>
                    <p className="text-2xl font-bold text-yellow-800">{highRisk}</p>
                </div>
                <div className="p-2 bg-red-100 rounded">
                    <p className="text-sm text-red-800">Critical</p>
                    <p className="text-2xl font-bold text-red-800">{criticalRisk}</p>
                </div>
            </div>
        </div>
    );
};

export default RiskSummary;
