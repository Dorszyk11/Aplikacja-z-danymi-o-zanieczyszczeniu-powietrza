import requests

class AirQualityAPIClient:
    def __init__(self, external_api_base, api_key, backend_api_endpoint):
        self.external_api_base = external_api_base
        self.api_key = api_key
        self.backend_api_endpoint = backend_api_endpoint

    def get_stations(self, city):
        params = {
            'city': city,
            'key': self.api_key
        }
        response = requests.get(f"{self.external_api_base}/v2/city", params=params)
        if response.status_code == 200:
            return response.json()['data']
        else:
            response.raise_for_status()

    def get_air_quality_data(self, station_id):
        params = {
            'key': self.api_key 
        }
        response = requests.get(f"{self.external_api_base}/v2/station/{station_id}", params=params)
        if response.status_code == 200:
            return response.json()['data']
        else:
            response.raise_for_status()

    def send_data_to_backend(self, data):
        # Wysyłanie danych do backendu
        response = requests.post(self.backend_api_endpoint, json=data)
        if response.status_code in [200, 201]:
            print("Data successfully sent to backend.")
        else:
            print(f"Failed to send data to backend, status code: {response.status_code}")
            response.raise_for_status()

external_api_base = "http://api.airvisual.com"  
api_key = "YOUR_API_KEY"  
backend_api_endpoint = "http://127.0.0.1:5000/data" 
city = "Warsaw" 

client = AirQualityAPIClient(external_api_base, api_key, backend_api_endpoint)
stations = client.get_stations(city)
if stations:
    for station in stations:
        air_quality_data = client.get_air_quality_data(station['id'])
        client.send_data_to_backend(air_quality_data)
