from flask import Flask, request, jsonify, send_from_directory
from database import get_recordings, delete_recording, init_db
import os

app = Flask(__name__, static_folder='static')

# Initialiser la base de données
init_db()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/recordings', methods=['GET'])
def list_recordings():
    recordings = get_recordings()
    return jsonify(recordings)

@app.route('/recordings/<int:recording_id>', methods=['DELETE'])
def remove_recording(recording_id):
    delete_recording(recording_id)
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)