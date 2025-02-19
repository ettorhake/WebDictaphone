import sqlite3

def init_db():
    conn = sqlite3.connect('recordings.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS recordings (
            id INTEGER PRIMARY KEY,
            filename TEXT,
            timestamp TEXT,
            transcription TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_recording(filename, timestamp, transcription=None):
    conn = sqlite3.connect('recordings.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO recordings (filename, timestamp, transcription)
        VALUES (?, ?, ?)
    ''', (filename, timestamp, transcription))
    conn.commit()
    conn.close()

def get_recordings():
    conn = sqlite3.connect('recordings.db')
    c = conn.cursor()
    c.execute('SELECT * FROM recordings')
    recordings = c.fetchall()
    conn.close()
    return recordings

def delete_recording(recording_id):
    conn = sqlite3.connect('recordings.db')
    c = conn.cursor()
    c.execute('DELETE FROM recordings WHERE id = ?', (recording_id,))
    conn.commit()
    conn.close()