import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS recordings
                 (id INTEGER PRIMARY KEY, filename TEXT, timestamp TEXT, client_ip TEXT, transcription TEXT)''')
    conn.commit()
    conn.close()

def add_recording(filename, timestamp, client_ip):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO recordings (filename, timestamp, client_ip) VALUES (?, ?, ?)", (filename, timestamp, client_ip))
    conn.commit()
    conn.close()

def get_recordings():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, filename, timestamp, client_ip, transcription FROM recordings")
    recordings = c.fetchall()
    conn.close()
    return [{'id': row[0], 'filename': row[1], 'timestamp': row[2], 'client_ip': row[3], 'transcription': row[4]} for row in recordings]

def delete_recording(recording_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM recordings WHERE id = ?", (recording_id,))
    conn.commit()
    conn.close()

def update_transcription(filename, transcription):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE recordings SET transcription = ? WHERE filename = ?", (transcription, filename))
    conn.commit()
    conn.close()