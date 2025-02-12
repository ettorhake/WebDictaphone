const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const app = express();
const port = 3000;

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        cb(null, `${Date.now()}-${file.originalname}`);
    }
});
const upload = multer({ storage });

// Serve static files from the "src" directory
app.use(express.static(path.join(__dirname, 'src')));

// Serve static files from the "uploads" directory
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Endpoint to handle file uploads
app.post('/upload', upload.single('audio'), (req, res) => {
    res.json({ filePath: `/uploads/${req.file.filename}` });
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

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});