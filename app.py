from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

data_storage = []

@app.route('/')
def index():
    return 'Witaj w aplikacji monitorującej jakość powietrza!'

@app.route('/data', methods=['POST'])
def save_data():
    data = request.json
    data_storage.append(data)
    print(data_storage)
    return jsonify({'status': 'success'}), 201



@app.route('/data', methods=['GET'])
def get_data():
    return jsonify(data_storage)


if __name__ == '__main__':
    app.run(debug=True)
