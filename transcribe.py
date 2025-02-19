import sys
import json
import os
import logging
import whisper
from pydub import AudioSegment
from pydub.utils import which
from database import add_recording, init_db

# Configurer le journalisation
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialiser la base de données
init_db()

# Spécifiez le chemin de ffmpeg et ffprobe si nécessaire
ffmpeg_path = which("ffmpeg") or "C:/path/to/ffmpeg/bin/ffmpeg.exe"
ffprobe_path = which("ffprobe") or "C:/path/to/ffmpeg/bin/ffprobe.exe"
AudioSegment.converter = ffmpeg_path
AudioSegment.ffmpeg = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

def transcribe_audio(file_path, output_path):
    logging.debug(f'Transcription du fichier audio : {file_path}')
    
    # Charger le modèle Whisper
    model = whisper.load_model("base")
    logging.debug('Modèle Whisper chargé.')

    # Charger le fichier audio en utilisant pydub
    audio = AudioSegment.from_file(file_path, format="webm", parameters=["-analyzeduration", "100M", "-probesize", "100M"])
    logging.debug('Audio chargé avec succès.')
    
    audio = audio.set_channels(1)  # Assurer un canal mono
    audio = audio.set_frame_rate(16000)  # Assurer un taux d'échantillonnage de 16 kHz
    logging.debug('Format audio modifié pour être mono et 16 kHz.')
    
    # Exporter l'audio en format WAV pour Whisper
    temp_wav_path = "temp_audio.wav"
    audio.export(temp_wav_path, format="wav")
    logging.debug('Audio exporté en format WAV.')

    # Transcrire l'audio avec Whisper
    result = model.transcribe(temp_wav_path, language="fr")
    logging.debug(f'Résultat de la transcription : {result["text"]}')
    
    # Écrire la transcription dans un fichier de sortie
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
    logging.debug(f'Transcription écrite dans le fichier : {output_path}')

    # Ajouter l'enregistrement à la base de données
    timestamp = os.path.basename(file_path).split('-')[1]
    add_recording(file_path, timestamp, result["text"])

    return result

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <audio_file_path> <output_file_path>")
    else:
        file_path = sys.argv[1]
        output_path = sys.argv[2]
        logging.debug(f'Début de la transcription pour le fichier : {file_path}')
        transcription = transcribe_audio(file_path, output_path)
        print(json.dumps(transcription, ensure_ascii=False))
        logging.debug('Transcription terminée.')