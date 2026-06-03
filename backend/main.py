from fastapi import FastAPI, UploadFile, File, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import uuid
import asyncio
from .config import UPLOAD_DIR, OUTPUT_DIR
from .ffmpeg_processor import FFmpegProcessor

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for job statuses
jobs = {}

@app.post("/api/upload/video")
async def upload_video(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_ext = os.path.splitext(file.filename)[1]
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}{file_ext}")
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"file_id": file_id, "file_path": file_path}

@app.post("/api/upload/srt")
async def upload_srt(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}.srt")
    with open(file_path, "wb") as f:
        f.write(await file.read())
    return {"file_id": file_id, "file_path": file_path}

@app.post("/api/auto-recap")
async def trigger_recap(
    background_tasks: BackgroundTasks,
    video_path: str = Form(...),
    srt_path: str = Form(...),
    duration: int = Form(...),
    fontSize: str = Form(...),
    fontColor: str = Form(...)
):
    job_id = str(uuid.uuid4())
    processor = FFmpegProcessor(job_id)
    jobs[job_id] = processor
    
    style_settings = {
        "fontSize": fontSize,
        "fontColor": fontColor
    }
    
    background_tasks.add_task(
        processor.process_recap, 
        video_path, 
        srt_path, 
        duration, 
        style_settings
    )
    
    return {"job_id": job_id}

@app.get("/api/recap/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        return {"error": "Job not found"}
    
    processor = jobs[job_id]
    return {
        "status": processor.status,
        "progress": processor.progress,
        "logs": processor.logs,
        "video_url": f"/outputs/recap_{job_id}.mp4" if processor.status == "completed" else None
    }

# Serve static files for frontend and outputs
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")
from .config import BASE_DIR
app.mount("/", StaticFiles(directory=os.path.join(os.path.dirname(BASE_DIR), "frontend"), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
