from flask import Flask, request, jsonify
from flask.views import MethodView
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ValidationError

app = Flask(__name__)

class DataStorage:
    def __init__(self):
        self.records: List['WeatherAndAirQualityData'] = []

    def add_record(self, record: 'WeatherAndAirQualityData') -> None:
        self.records.append(record)

    def find_closest_record(self, timestamp: datetime) -> Optional['WeatherAndAirQualityData']:
        if not self.records:
            return None
        return min(self.records, key=lambda x: abs(x.timestamp - timestamp))

class WeatherAndAirQualityData(BaseModel):
    timestamp: datetime
    temperature: Optional[int] = Field(None, ge=-50, le=50)
    pressure: Optional[int] = Field(None, ge=800, le=1200)
    humidity: Optional[int] = Field(None, ge=0, le=100)
    aqi: Optional[int] = Field(None, ge=0)

class DataRecordView(MethodView):
    def get(self):
        timestamp_query = request.args.get('timestamp')
        if not timestamp_query:
            return jsonify({"error": "Timestamp query parameter is required."}), 400

        try:
            query_timestamp = datetime.fromisoformat(timestamp_query)
        except ValueError:
            return jsonify({"error": "Invalid timestamp format."}), 400
        
        closest_record = storage.find_closest_record(query_timestamp)
        if closest_record:
            return jsonify(closest_record.dict()), 200
        return jsonify({"message": "No data found."}), 404

    def post(self):
        data = request.json
        try:
            record = WeatherAndAirQualityData(**data)
        except ValidationError as e:
            return jsonify({"error": str(e)}), 400
        
        storage.add_record(record)
        return jsonify(record.dict()), 201

def configure_routes(app: Flask):
    app.add_url_rule('/data', view_func=DataRecordView.as_view('data_api'))

storage = DataStorage()

if __name__ == '__main__':
    configure_routes(app)
    app.run(debug=True)
