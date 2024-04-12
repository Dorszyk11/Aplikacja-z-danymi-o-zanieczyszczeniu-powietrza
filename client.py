import requests

class AirQualityClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.airvisual.com/v2"
    
    def get_station_air_quality(self, city: str, state: str, country: str) -> dict:
        endpoint = f"{self.base_url}/city?city={city}&state={state}&country={country}&key={self.api_key}"
        response = requests.get(endpoint)
        if response.ok:
            return response.json()
        else:
            raise Exception(f"API request failed with status code {response.status_code}")

    def validate_and_format_data(self, data):
        """ Validates and formats the data before sending it to the backend """
        if 'data' not in data:
            raise ValueError("Invalid data structure")
        
        temp = data['data']['current']['weather']['tp']
        pressure = data['data']['current']['weather']['pr']
        if not (-50 <= temp <= 50):
            raise ValueError("Invalid temperature value")
        if not (900 <= pressure <= 1100):
            raise ValueError("Invalid pressure value")
        
        formatted_data = {
            'city': "Warsaw",
            'state': "Mazovia",
            'country': "Poland",
            'temperature': temp,
            'pressure': pressure,
            'air_quality_index': data['data']['current']['pollution']['aqius'],
            'timestamp': data['data']['current']['weather']['ts']
        }
        return formatted_data

    def send_data_to_backend(self, data, backend_url):
        """ Sends the data to the backend server """
        response = requests.post(backend_url, json=data)
        if response.status_code == 201:
            print("Data sent successfully")
        else:
            print(f"Failed to send data: {response.status_code}")

if __name__ == "__main__":
    api_key = "fd2bef12-6cbd-46f0-a58e-3c45bb93f036"
    backend_url = "http://localhost:5000/data"
    client = AirQualityClient(api_key)
    try:
        air_quality_data = client.get_station_air_quality("Warsaw", "Mazovia", "Poland")
        formatted_data = client.validate_and_format_data(air_quality_data)
        client.send_data_to_backend(formatted_data, backend_url)
    except Exception as e:
        print(f"Error: {e}")
