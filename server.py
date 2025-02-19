from flask import Flask, request, jsonify, send_from_directory
from database import get_recordings, delete_recording, init_db
import os
import logging

app = Flask(__name__, static_folder='/var/www/WebDictaphone/static')

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

@app.route('/upload', methods=['POST'])
def upload_recording():
    if 'audio' not in request.files:
        return jsonify(success=False, message='No file part'), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify(success=False, message='No selected file'), 400

    filename = file.filename
    file.save(os.path.join(app.static_folder, filename))
    return jsonify(success=True, filePath=os.path.join(app.static_folder, filename))

if __name__ == '__main__':
    cert_path = '/etc/letsencrypt/live/rec.lauzesjulien.com/fullchain.pem'
    key_path = '/etc/letsencrypt/live/rec.lauzesjulien.com/privkey.pem'
    
    if os.path.exists(cert_path) and os.path.exists(key_path):
        context = (cert_path, key_path)
        logging.debug(f'Certificat trouvé. Lancement du serveur en HTTPS sur le port 3443.')
        app.run(debug=True, host='0.0.0.0', port=3443, ssl_context=context)  # Utiliser HTTPS
    else:
        logging.debug(f'Certificat non trouvé. Lancement du serveur en HTTP sur le port 5000.')
        app.run(debug=True, host='0.0.0.0', port=5000)  # Utiliser HTTP