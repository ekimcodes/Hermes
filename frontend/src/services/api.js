import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8081/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getHealth = async () => {
    try {
        const response = await axios.get('http://localhost:8081/health');
        return response.data;
    } catch (error) {
        console.error("Health check failed:", error);
        return { status: "unhealthy" };
    }
};

export const predictOutages = async (feederIds, weatherOverride = null) => {
    try {
        const payload = { feeder_ids: feederIds };
        if (weatherOverride) {
            payload.weather_override = weatherOverride;
        }
        const response = await api.post('/predict', payload);
        return response.data;
    } catch (error) {
        console.error('Prediction failed:', error);
        throw error;
    }
};

export default api;
