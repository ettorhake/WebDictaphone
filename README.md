# Dictaphone Web Application

This is a simple web application that allows users to record audio using their device's microphone. The application starts recording automatically when the page is loaded and stops recording after a period of silence or when the user clicks the "Stop Recording" button. The recorded audio files are saved on the server and can be played back directly in the browser. The application also displays the audio waveform and the average audio level in real-time.

## Features

- Automatically starts recording when the page is loaded.
- Starts recording when the average audio level exceeds 70.
- Stops recording after 10 seconds of silence (average audio level below 70).
- Allows manual stopping of the recording with a "Stop Recording" button.
- Displays the audio waveform in real-time.
- Displays the average audio level in real-time.
- Saves recorded audio files in MP3 format with a timestamp.
- Lists recorded audio files in a table, sortable by date.
- Allows playback of recorded audio files directly in the browser.
- Allows deletion of recorded audio files from the browser.
- Stores recorded audio files on the server.
- Transcribes recorded audio files to text using Vosk.
- Allows searching for keywords in transcriptions and returns timestamps of occurrences.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/dictaphone-web-app.git
    ```
2. Navigate to the project directory:
    ```sh
    cd dictaphone-web-app
    ```
3. Install the necessary Node.js dependencies:
    ```sh
    npm install
    ```
4. Install the necessary Python dependencies:
    ```sh
    pip install vosk soundfile pydub
    ```
5. Download the French language model for Vosk from [the official site](https://alphacephei.com/vosk/models) and extract it to a directory of your choice. Update the path to the model in the `transcribe.py` script.

6. Generate SSL certificates (for development purposes):
    ```sh
    openssl genrsa -out key.pem 2048
    openssl req -new -key key.pem -out csr.pem
    openssl x509 -req -days 365 -in csr.pem -signkey key.pem -out cert.pem
    ```

## Usage

1. Start the server:
    ```sh
    node server.js
    ```
2. Open your web browser and navigate to `http://localhost:3000` for HTTP or `https://localhost:3443` for HTTPS (if SSL certificates are available).
3. The application will start recording automatically when the average audio level exceeds 70.
4. Click the "Stop Recording" button to manually stop the recording and start a new one.
5. View the recorded audio files in the table, play them back, and delete them directly in the browser.
6. Click the "Transcribe" button to transcribe the recorded audio file. The status of the transcription will be displayed.
7. Use the `/search` endpoint to search for keywords in transcriptions and get the timestamps of occurrences. For example:
    ```
    GET /search?keyword=bonjour
    ```

## Dependencies

- Node.js
- Express
- Multer
- Python
- Vosk
- Soundfile
- Pydub

## License

This project is licensed under the MIT License. See the LICENSE file for details.