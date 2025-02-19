from flask import Flask, request, jsonify, send_from_directory
from database import get_recordings, delete_recording, init_db
import os
import logging

app = Flask(__name__, static_folder='static')

# Configurer le journalisation
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

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
    cert_path = '...'
    key_path = '...'
    
    if os.path.exists(cert_path) and os.path.exists(key_path):
        context = (cert_path, key_path)
        logging.debug(f'Certificat trouvé. Lancement du serveur en HTTPS sur le port 3443.')
        app.run(debug=True, port=3443, ssl_context=context)  # Utiliser HTTPS
    else:
        logging.debug(f'Certificat non trouvé. Lancement du serveur en HTTP sur le port 5000.')
        app.run(debug=True, port=5000)  # Utiliser HTTP