import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# FFmpeg Optimization Profiles
FFMPEG_PROFILES = {
    "low": {
        "video_bitrate": "1000k",
        "preset": "ultrafast",
        "crf": "28"
    },
    "medium": {
        "video_bitrate": "2500k",
        "preset": "medium",
        "crf": "23"
    },
    "high": {
        "video_bitrate": "5000k",
        "preset": "slow",
        "crf": "18"
    }
}
