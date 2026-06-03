const urlParams = new URLSearchParams(window.location.search);
const jobId = urlParams.get('job_id');

const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const terminal = document.getElementById('terminal');
const resultSection = document.getElementById('resultSection');
const videoPlayer = document.getElementById('videoPlayer');
const downloadBtn = document.getElementById('downloadBtn');

let lastLogCount = 0;

async function pollStatus() {
    if (!jobId) return;

    try {
        const response = await fetch(`/api/recap/status/${jobId}`);
        const data = await response.json();

        if (data.error) {
            addLog(`[ERROR] ${data.error}`);
            return;
        }

        // Update Progress
        progressBar.style.width = `${data.progress}%`;
        progressText.innerText = `${data.progress}%`;

        // Update Logs
        if (data.logs.length > lastLogCount) {
            for (let i = lastLogCount; i < data.logs.length; i++) {
                addLog(`[BACKEND] ${data.logs[i]}`);
            }
            lastLogCount = data.logs.length;
        }

        if (data.status === 'completed') {
            clearInterval(pollInterval);
            showResult(data.video_url);
        } else if (data.status === 'failed') {
            clearInterval(pollInterval);
            addLog('[SYSTEM] Process failed. Check logs above.');
        }

    } catch (error) {
        console.error('Polling error:', error);
    }
}

function addLog(message) {
    const div = document.createElement('div');
    div.innerText = message;
    terminal.appendChild(div);
    terminal.scrollTop = terminal.scrollHeight;
}

function showResult(videoUrl) {
    resultSection.style.display = 'block';
    videoPlayer.src = videoUrl;
    downloadBtn.href = videoUrl;
    addLog('[SYSTEM] All processes finished. Preview ready.');
}

const pollInterval = setInterval(pollStatus, 2000);
pollStatus(); // Initial call
