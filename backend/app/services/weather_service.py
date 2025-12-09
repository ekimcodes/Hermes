import httpx
from typing import Dict, Any, List

class WeatherService:
    def __init__(self):
        self.base_url = "https://api.open-meteo.com/v1/forecast"
    
    async def get_current_weather(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        Fetch current weather data for a specific location using Open-Meteo API.
        """
        return (await self.get_current_weather_batch([latitude], [longitude]))[0]

    async def get_current_weather_batch(self, latitudes: List[float], longitudes: List[float]) -> List[Dict[str, Any]]:
        """
        Fetch current weather data for multiple locations in a single API call.
        """
        if not latitudes or not longitudes:
            return []

        params = {
            "latitude": ",".join(map(str, latitudes)),
            "longitude": ",".join(map(str, longitudes)),
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation",
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # Open-Meteo handles comma-separated lists automatically
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # If requesting single location, data is a dict. If multiple, it is a list of dicts.
                if isinstance(data, dict):
                    data = [data] # Normalize to list
                
                results = []
                for item in data:
                    current = item.get("current", {})
                    results.append({
                        "temperature": current.get("temperature_2m", 70.0),
                        "humidity": current.get("relative_humidity_2m", 50.0),
                        "wind_speed": current.get("wind_speed_10m", 5.0),
                        "precipitation": current.get("precipitation", 0.0)
                    })
                return results

            except Exception as e:
                print(f"Error fetching batch weather data: {e}")
                # Fallback: return default for every requested point
                return [{
                    "temperature": 70.0,
                    "humidity": 50.0,
                    "wind_speed": 5.0,
                    "precipitation": 0.0
                } for _ in latitudes]

weather_service = WeatherService()
