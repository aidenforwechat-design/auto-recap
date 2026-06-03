const videoDropzone = document.getElementById('videoDropzone');
const srtDropzone = document.getElementById('srtDropzone');
const videoInput = document.getElementById('videoInput');
const srtInput = document.getElementById('srtInput');
const triggerBtn = document.getElementById('triggerBtn');

let videoPath = '';
let srtPath = '';

// Helper for file uploads
async function uploadFile(file, type) {
    const formData = new FormData();
    formData.append('file', file);
    
    const endpoint = type === 'video' ? '/api/upload/video' : '/api/upload/srt';
    const statusEl = document.getElementById(`${type}Status`);
    
    statusEl.innerText = 'Uploading...';
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        statusEl.innerText = `Uploaded: ${file.name}`;
        return data.file_path;
    } catch (error) {
        statusEl.innerText = 'Upload failed.';
        console.error(error);
        return null;
    }
}

// Drag & Drop Handlers
videoDropzone.onclick = () => videoInput.click();
srtDropzone.onclick = () => srtInput.click();

videoInput.onchange = async (e) => {
    if (e.target.files.length) {
        videoPath = await uploadFile(e.target.files[0], 'video');
    }
};

srtInput.onchange = async (e) => {
    if (e.target.files.length) {
        srtPath = await uploadFile(e.target.files[0], 'srt');
    }
};

// Trigger Pipeline
triggerBtn.onclick = async () => {
    if (!videoPath || !srtPath) {
        alert('Please upload both video and SRT files first.');
        return;
    }

    const duration = document.getElementById('duration').value;
    const fontSize = document.getElementById('fontSize').value;
    const fontColor = document.getElementById('fontColor').value;

    const formData = new FormData();
    formData.append('video_path', videoPath);
    formData.append('srt_path', srtPath);
    formData.append('duration', duration);
    formData.append('fontSize', fontSize);
    formData.append('fontColor', fontColor);

    try {
        const response = await fetch('/api/auto-recap', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (data.job_id) {
            window.location.href = `preview.html?job_id=${data.job_id}`;
        }
    } catch (error) {
        alert('Failed to start recap process.');
        console.error(error);
    }
};
