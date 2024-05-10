from flask import Flask, request, jsonify
from flask.views import MethodView
from datetime import datetime, timezone
from typing import Optional, List
import pydantic

app = Flask(__name__)

def normalize_datetime(dt):
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

class DataStorage:
    def __init__(self):
        self.records: List[WeatherAndAirQualityData] = []

    def add_record(self, record):
        self.records.append(record)

    def find_closest_record(self, timestamp: datetime):
        normalized_timestamp = normalize_datetime(timestamp)
        try:
            return min(
                self.records,
                key=lambda x: abs(normalize_datetime(x.timestamp) - normalized_timestamp),
                default=None
            )
        except ValueError:
            return None

class WeatherAndAirQualityData(pydantic.BaseModel):
    timestamp: datetime
    temperature: Optional[int] = pydantic.Field(None, ge=-50, le=50)
    pressure: Optional[int] = pydantic.Field(None, ge=800, le=1200)
    air_quality_index: Optional[int] = pydantic.Field(None, ge=0)
    city: str
    state: str
    country: str

class AirQualityDataView(MethodView):
    def get(self):
        timestamp_query = request.args.get('timestamp')
        if timestamp_query:
            try:
                query_timestamp = normalize_datetime(datetime.fromisoformat(timestamp_query))
                closest_record = storage.find_closest_record(query_timestamp)
                return jsonify(closest_record.dict()) if closest_record else jsonify({"message": "No data found."}), 404
            except ValueError:
                return jsonify({"error": "Invalid timestamp format"}), 400
        else:
            all_records = [record.dict() for record in storage.records]
            return jsonify(all_records)

    def post(self):
        data = request.json
        try:
            timestamp_str = data['timestamp']
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1]  # Remove the 'Z'
            data['timestamp'] = normalize_datetime(datetime.fromisoformat(timestamp_str).replace(tzinfo=timezone.utc))
            record = WeatherAndAirQualityData(**data)
            storage.add_record(record)
            return jsonify(record.dict()), 201
        except pydantic.ValidationError as e:
            return jsonify({"error": str(e)}), 400
        except ValueError as e:
            return jsonify({"error": "Invalid datetime format"}), 400

storage = DataStorage()

app.add_url_rule('/data', view_func=AirQualityDataView.as_view('data_api'))

if __name__ == '__main__':
    app.run(debug=True)
 