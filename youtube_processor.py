import re
import os
import tempfile
import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi
from faster_whisper import WhisperModel


class YouTubeProcessor:

    def __init__(self):
        print("⚡ Loading Whisper model...")
        self.model = WhisperModel("base", device="cpu")
        print("✅ Whisper ready")

    # 🔍 EXTRACT VIDEO ID
    def extract_video_id(self, url):
        match = re.search(r"(v=|youtu\.be\/)([0-9A-Za-z_-]{11})", url)
        return match.group(2) if match else None

    # ⚡ TRY TRANSCRIPT API
    def get_fast_transcript(self, video_id):
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return " ".join([t["text"] for t in transcript])
        except:
            return None

    # 🎧 DOWNLOAD AUDIO
    def download_audio(self, url, out_dir):
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{out_dir}/%(id)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        for f in os.listdir(out_dir):
            if f.endswith(".mp3"):
                return os.path.join(out_dir, f)

        return None

    # 🧠 WHISPER TRANSCRIPTION
    def transcribe(self, audio_path):
        segments, _ = self.model.transcribe(audio_path)
        return " ".join([seg.text for seg in segments])

    # 🔥 BEST TRANSCRIPT (NO FAIL SYSTEM)
    def get_best_transcript(self, url):
        video_id = self.extract_video_id(url)

        # 1️⃣ TRY FAST API
        text = self.get_fast_transcript(video_id)
        if text:
            print("⚡ Transcript API success")
            return text

        print("🐢 Falling back to Whisper...")

        # 2️⃣ FALLBACK → DOWNLOAD + WHISPER
        with tempfile.TemporaryDirectory() as tmp:
            audio = self.download_audio(url, tmp)

            if not audio:
                raise Exception("Audio download failed")

            text = self.transcribe(audio)

        return text

    # 🎬 VIDEO INFO
    def get_video_details(self, url):
        try:
            with yt_dlp.YoutubeDL() as ydl:
                info = ydl.extract_info(url, download=False)

                return {
                    "title": info.get("title"),
                    "channel": info.get("uploader")
                }
        except:
            return {"title": "Unknown", "channel": "Unknown"}