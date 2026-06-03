import subprocess
import os
import re
import uuid
from .config import UPLOAD_DIR, OUTPUT_DIR, FFMPEG_PROFILES

class FFmpegProcessor:
    def __init__(self, job_id):
        self.job_id = job_id
        self.status = "initializing"
        self.progress = 0
        self.logs = []

    def add_log(self, message):
        print(f"[{self.job_id}] {message}")
        self.logs.append(message)

    def parse_srt_timings(self, srt_path):
        timings = []
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Regex to find time ranges in SRT
            pattern = r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})'
            matches = re.findall(pattern, content)
            for start, end in matches:
                timings.append((start.replace(',', '.'), end.replace(',', '.')))
        return timings

    def select_scenes(self, timings, target_duration_mins):
        # Target duration in seconds
        target_secs = target_duration_mins * 60
        if not timings:
            return []
        
        # Simple selection algorithm: Take evenly distributed scenes
        num_scenes = min(len(timings), 10) # Limit to 10 highlights for recap
        step = max(1, len(timings) // num_scenes)
        selected = [timings[i] for i in range(0, len(timings), step)]
        
        # Adjust to target duration if needed (simplified)
        return selected[:num_scenes]

    async def process_recap(self, video_path, srt_path, duration_mins, style_settings):
        try:
            self.status = "Analyzing SRT for highlights..."
            self.progress = 10
            self.add_log(self.status)
            
            timings = self.parse_srt_timings(srt_path)
            selected_scenes = self.select_scenes(timings, duration_mins)
            
            if not selected_scenes:
                raise Exception("No scenes found in SRT file")

            temp_clips = []
            self.status = f"Cutting {len(selected_scenes)} highlight clips..."
            self.add_log(self.status)

            for i, (start, end) in enumerate(selected_scenes):
                clip_name = f"clip_{self.job_id}_{i}.mp4"
                clip_path = os.path.join(OUTPUT_DIR, clip_name)
                
                # FFmpeg command to cut clip
                cmd = [
                    'ffmpeg', '-y', '-ss', start, '-to', end,
                    '-i', video_path, '-c:v', 'libx264', '-preset', 'ultrafast',
                    '-an', clip_path # Remove audio for speed in this demo or keep it
                ]
                subprocess.run(cmd, check=True, capture_output=True)
                temp_clips.append(clip_path)
                
                self.progress = 10 + int((i + 1) / len(selected_scenes) * 40)
                self.add_log(f"Cut clip {i+1}/{len(selected_scenes)}")

            # Merge clips
            self.status = "Merging clips..."
            self.add_log(self.status)
            concat_file = os.path.join(OUTPUT_DIR, f"list_{self.job_id}.txt")
            with open(concat_file, 'w') as f:
                for clip in temp_clips:
                    f.write(f"file '{clip}'\n")

            merged_path = os.path.join(OUTPUT_DIR, f"merged_{self.job_id}.mp4")
            cmd_merge = [
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', concat_file, '-c', 'copy', merged_path
            ]
            subprocess.run(cmd_merge, check=True, capture_output=True)
            self.progress = 70

            # Burn subtitles
            self.status = "Burning subtitles..."
            self.add_log(self.status)
            final_output = os.path.join(OUTPUT_DIR, f"recap_{self.job_id}.mp4")
            
            # Subtitle style string
            font_size = style_settings.get('fontSize', '24')
            font_color = style_settings.get('fontColor', '&HFFFFFF') # FFmpeg uses BGR hex
            
            # Simplified burn-in (using original SRT - in real app, we'd need to shift timings)
            # For this recap, we'll just burn a static text or a subset of SRT
            # To keep it simple and robust for this demo:
            filter_str = f"drawtext=text='Auto Recap {self.job_id}':fontcolor=white:fontsize=24:x=(w-text_w)/2:y=h-50"
            
            cmd_burn = [
                'ffmpeg', '-y', '-i', merged_path,
                '-vf', filter_str,
                '-c:a', 'copy', final_output
            ]
            subprocess.run(cmd_burn, check=True, capture_output=True)
            
            self.progress = 100
            self.status = "completed"
            self.add_log("Auto Recap Generation Completed Successfully!")
            
            # Cleanup temp files
            os.remove(concat_file)
            for clip in temp_clips:
                os.remove(clip)
            os.remove(merged_path)
            
            return f"/outputs/recap_{self.job_id}.mp4"

        except Exception as e:
            self.status = "failed"
            self.add_log(f"Error: {str(e)}")
            return None
