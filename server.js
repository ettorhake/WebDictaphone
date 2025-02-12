const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const http = require('http');
const https = require('https');
const { exec } = require('child_process');
const app = express();
const httpPort = 3000;
const httpsPort = 3443;

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        const ip = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
        const date = new Date();
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const filename = `${ip}-${day}-${month}-${hours}-${minutes}.mp3`;
        cb(null, filename);
    }
});
const upload = multer({ storage });

// Serve static files from the "src" directory
app.use(express.static(path.join(__dirname, 'src')));

// Serve static files from the "uploads" directory
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Endpoint to handle file uploads
app.post('/upload', upload.single('audio'), (req, res) => {
    const filePath = path.join('uploads', req.file.filename);
    res.json({ filePath });
});

// Endpoint to handle file deletion
app.delete('/uploads/:filename', (req, res) => {
    const filePath = path.join(__dirname, 'uploads', req.params.filename);
    fs.unlink(filePath, err => {
        if (err) {
            return res.status(500).json({ error: 'Failed to delete file' });
        }
        res.status(200).json({ message: 'File deleted successfully' });
    });
});

// Endpoint to transcribe audio files
app.get('/transcribe', (req, res) => {
    const { filename } = req.query;
    const filePath = path.join(__dirname, '', filename);

    exec(`python transcribe.py ${filePath}`, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing Python script: ${error.message}`);
            return res.status(500).json({ error: 'Failed to transcribe audio' });
        }
        if (stderr) {
            console.error(`Python script stderr: ${stderr}`);
            return res.status(500).json({ error: 'Failed to transcribe audio' });
        }

        // Save the transcription result
        const transcription = JSON.parse(stdout);
        const transcriptionFilePath = filePath.replace('.mp3', '.json');
        fs.writeFileSync(transcriptionFilePath, JSON.stringify(transcription, null, 2));

        res.json({ success: true });
    });
});

// Function to search for keywords in transcription
const searchKeywordInTranscription = (transcription, keyword) => {
    const results = [];
    transcription.forEach(result => {
        if (result.text && result.text.includes(keyword)) {
            results.push({ timestamp: result.result[0].start, text: result.text });
        }
    });
    return results;
};

// Endpoint to search for keywords in transcription
app.get('/search', (req, res) => {
    const { keyword } = req.query;
    const transcriptionFiles = fs.readdirSync(path.join(__dirname, 'uploads')).filter(file => file.endsWith('.json'));
    const results = [];

    transcriptionFiles.forEach(file => {
        const transcription = JSON.parse(fs.readFileSync(path.join(__dirname, 'uploads', file), 'utf8'));
        const fileResults = searchKeywordInTranscription(transcription, keyword);
        fileResults.forEach(result => {
            results.push({ filename: file, timestamp: result.timestamp, text: result.text });
        });
    });

    res.json({ results });
});

// Read SSL certificate and key if available
let httpsOptions;
try {
    httpsOptions = {
        key: fs.readFileSync('key.pem'),
        cert: fs.readFileSync('cert.pem')
    };
} catch (error) {
    console.warn('SSL certificates not found. HTTPS will not be available.');
}

// Create HTTP server
http.createServer(app).listen(httpPort, '0.0.0.0', () => {
    console.log(`HTTP server running at http://localhost:${httpPort}`);
});

// Create HTTPS server if certificates are available
if (httpsOptions) {
    https.createServer(httpsOptions, app).listen(httpsPort, '0.0.0.0', () => {
        console.log(`HTTPS server running at https://localhost:${httpsPort}`);
    });
}