from flask import Flask, request, jsonify, send_from_directory
from database import get_recordings, delete_recording, init_db, add_recording, update_transcription
import os
import logging
from datetime import datetime

app = Flask(__name__, static_folder=r'C:\Users\Jlauzes\Dropbox\DOCUMENT PRIVE\INTERNET\HACK\WebDictaphone\static')

# Configurer le journalisation
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialiser la base de données
# Créer le dossier uploads avec les bonnes autorisations
uploads_folder = os.path.join(os.path.dirname(app.static_folder), 'uploads')
if not os.path.exists(uploads_folder):
    os.makedirs(uploads_folder, exist_ok=True)
    os.chmod(uploads_folder, 0o755)

# Ajouter la configuration du dossier de téléchargement
app.config['UPLOAD_FOLDER'] = uploads_folder

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
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    app.logger.debug(f'File saved: {filename}')  # Ajoutez cette ligne

    # Ajouter l'enregistrement à la base de données
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    client_ip = request.remote_addr
    add_recording(filename, timestamp, client_ip)

    return jsonify(success=True, filePath=file_path)

@app.route('/uploads/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/transcribe', methods=['GET'])
def transcribe_recording():
    filename = request.args.get('filename')
    if not filename:
        return jsonify(success=False, message='No filename provided'), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        return jsonify(success=False, message='File not found'), 404

    # Simuler la transcription (vous pouvez remplacer cette partie par votre propre logique de transcription)
    transcription = f"Transcription of {filename}"

    # Mettre à jour la base de données avec la transcription
    update_transcription(filename, transcription)

    return jsonify(success=True, transcription=transcription)

if __name__ == '__main__':
    cert_path = '/etc/letsencrypt/live/rec.lauzesjulien.com/fullchain.pem'
    key_path = '/etc/letsencrypt/live/rec.lauzesjulien.com/privkey.pem'
    
    if os.path.exists(cert_path) and os.path.exists(key_path):
        context = (cert_path, key_path)
        handler = logging.FileHandler('server.log')
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levellevel)s - %(message)s'))
        app.logger.addHandler(handler)
        logging.debug(f'Certificat trouvé. Lancement du serveur en HTTPS sur le port 3443.')
        app.run(debug=True, host='0.0.0.0', port=3443, ssl_context=context)  # Utiliser HTTPS
    else:
        logging.debug(f'Certificat non trouvé. Lancement du serveur en HTTP sur le port 5000.')
        app.run(debug=True, host='0.0.0.0', port=5000)  # Utiliser HTTP