import sys
import json
import os
import logging
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
from pydub.utils import which

# Configurer le journalisation
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Spécifiez le chemin de ffmpeg et ffprobe si nécessaire
ffmpeg_path = which("ffmpeg") or "C:/path/to/ffmpeg/bin/ffmpeg.exe"
ffprobe_path = which("ffprobe") or "C:/path/to/ffmpeg/bin/ffprobe.exe"
AudioSegment.converter = ffmpeg_path
AudioSegment.ffmpeg = ffmpeg_path
AudioSegment.ffprobe = ffprobe_path

def transcribe_audio(file_path):
    logging.debug(f'Transcription du fichier audio : {file_path}')
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, "src/vosk-model-small-fr-0.22/")
    logging.debug(f'Chemin du modèle : {model_path}')
    
    model = Model(model_path)

    # Charger le fichier WebM en utilisant pydub avec des options ffmpeg supplémentaires
    audio = AudioSegment.from_file(file_path, format="webm", parameters=["-analyzeduration", "100M", "-probesize", "100M"])
    logging.debug('Audio chargé avec succès.')
    
    audio = audio.set_channels(1)  # Assurer un canal mono
    audio = audio.set_frame_rate(16000)  # Assurer un taux d'échantillonnage de 16 kHz
    logging.debug('Format audio modifié pour être mono et 16 kHz.')
    
    # Convertir AudioSegment en données audio brutes
    raw_audio = audio.raw_data
    logging.debug('Données audio brutes obtenues.')

    rec = KaldiRecognizer(model, 16000)
    logging.debug('Reconnaissance Kaldi initialisée.')

    results = []
    if rec.AcceptWaveform(raw_audio):
        result = json.loads(rec.Result())
        results.append(result)
        logging.debug(f'Résultat de la reconnaissance : {result}')
    else:
        logging.warning('La reconnaissance n\'a pas pu être effectuée sur toute la forme d\'onde.')

    final_result = json.loads(rec.FinalResult())
    results.append(final_result)
    logging.debug(f'Résultat final de la reconnaissance : {final_result}')
    
    return results

if __name__ == "__main__":
    file_path = sys.argv[1]
    logging.debug(f'Début de la transcription pour le fichier : {file_path}')
    transcription = transcribe_audio(file_path)
    print(json.dumps(transcription, ensure_ascii=False))
    logging.debug('Transcription terminée.')
