document.addEventListener('DOMContentLoaded', async () => {
    const recordingsList = document.getElementById('recordingsList');
    const canvas = document.getElementById('visualizer');
    const canvasCtx = canvas.getContext('2d');
    const stopButton = document.getElementById('stopButton');
    const averageDisplay = document.getElementById('average'); // Element to display the average value
    const recorderStateDisplay = document.getElementById('recorderState'); // Element to display the recorder state
    let mediaRecorder;
    let audioChunks = [];
    let silenceTimeout;
    const startThreshold = 70; // Threshold to start recording
    const silenceDuration = 5000; // Duration of silence to stop recording (5 seconds)

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstart = () => {
        recorderStateDisplay.textContent = `State: ${mediaRecorder.state}`;
    };

    mediaRecorder.onstop = () => {
        recorderStateDisplay.textContent = `State: ${mediaRecorder.state}`;
        saveRecording();
    };

    const saveRecording = async () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const formData = new FormData();
        formData.append('audio', audioBlob, `recording-${timestamp}.webm`);

        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        const audioUrl = result.filePath;
        const a = document.createElement('a');
        a.href = audioUrl;
        a.download = `recording-${timestamp}.webm`;
        a.textContent = `Recording from ${timestamp}`;

        const audio = document.createElement('audio');
        audio.controls = true;
        audio.src = audioUrl;

        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.addEventListener('click', async () => {
            await fetch(audioUrl, { method: 'DELETE' });
            tr.remove();
        });

        const transcribeButton = document.createElement('button');
        transcribeButton.textContent = 'Transcribe';
        const transcriptionStatus = document.createElement('span');
        transcriptionStatus.textContent = 'Not started';
        transcribeButton.addEventListener('click', async () => {
            transcriptionStatus.textContent = 'In progress...';
            const transcribeResponse = await fetch(`/transcribe?filename=${result.filePath}`);
            const transcribeResult = await transcribeResponse.json();
            if (transcribeResult.success) {
                transcriptionStatus.textContent = 'Completed';
            } else {
                transcriptionStatus.textContent = 'Failed';
            }
        });

        const li = document.createElement('li');
        li.appendChild(a);
        li.appendChild(audio);

        const tr = document.createElement('tr');
        const tdDate = document.createElement('td');
        const tdRecording = document.createElement('td');
        const tdAction = document.createElement('td');
        const tdStatus = document.createElement('td');
        tdDate.textContent = new Date().toLocaleString('fr-FR');
        tdRecording.appendChild(li);
        tdAction.appendChild(deleteButton);
        tdAction.appendChild(transcribeButton);
        tdStatus.appendChild(transcriptionStatus);
        tr.appendChild(tdDate);
        tr.appendChild(tdRecording);
        tr.appendChild(tdAction);
        tr.appendChild(tdStatus);
        recordingsList.appendChild(tr);

        audioChunks = [];
    };

    const startRecording = () => {
        mediaRecorder.start();
        recorderStateDisplay.textContent = `State: ${mediaRecorder.state}`;
    };

    const stopRecording = () => {
        mediaRecorder.stop();
        recorderStateDisplay.textContent = `State: ${mediaRecorder.state}`;
    };

    const audioContext = new AudioContext();
    const analyser = audioContext.createAnalyser();
    const source = audioContext.createMediaStreamSource(stream);
    source.connect(analyser);
    analyser.fftSize = 2048;
    const bufferLength = analyser.fftSize;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
        requestAnimationFrame(draw);

        analyser.getByteTimeDomainData(dataArray);

        canvasCtx.fillStyle = 'rgb(200, 200, 200)';
        canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

        canvasCtx.lineWidth = 2;
        canvasCtx.strokeStyle = 'rgb(0, 0, 0)';

        canvasCtx.beginPath();

        const sliceWidth = canvas.width * 1.0 / bufferLength;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
            const v = dataArray[i] / 128.0;
            const y = v * canvas.height / 2;

            if (i === 0) {
                canvasCtx.moveTo(x, y);
            } else {
                canvasCtx.lineTo(x, y);
            }

            x += sliceWidth;
        }

        canvasCtx.lineTo(canvas.width, canvas.height / 2);
        canvasCtx.stroke();
    };

    draw();

    const detectSilence = () => {
        analyser.getByteFrequencyData(dataArray);
        const average = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
        averageDisplay.textContent = `Average: ${average.toFixed(2)}`; // Display the average value
        const isSilent = average < startThreshold;

        if (average > startThreshold && mediaRecorder.state === 'inactive') {
            startRecording();
        }

        if (isSilent && mediaRecorder.state === 'recording') {
            if (!silenceTimeout) {
                silenceTimeout = setTimeout(() => {
                    stopRecording();
                    silenceTimeout = null;
                }, silenceDuration); // Stop recording after 5 seconds of silence
            }
        } else if (!isSilent) {
            clearTimeout(silenceTimeout);
            silenceTimeout = null;
        }

        setTimeout(detectSilence, 1000); // Check for silence every second
    };

    detectSilence();

    stopButton.addEventListener('click', () => {
        clearTimeout(silenceTimeout);
        stopRecording();
    });
});