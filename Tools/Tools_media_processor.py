import os
import speech_recognition as sr
import subprocess
import logging
from Tools.Tools_setup_ffmpeg import FFmpegSetup

class MediaProcessor:
    @staticmethod
    def process_media_file(file_path: str, language='th-TH') -> str:
        """Process any media file (audio/video) to text"""
        if not FFmpegSetup.check_ffmpeg():
            raise ValueError("ไม่พบ FFmpeg กรุณารอสักครู่ระบบกำลังติดตั้งให้อัตโนมัติ")

        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_audio = os.path.join(temp_dir, "temp_audio.wav")

        try:
            # Extract/convert audio
            subprocess.run([
                'ffmpeg',
                '-i', file_path,
                '-vn',  # No video
                '-acodec', 'pcm_s16le',
                '-ar', '16000',
                '-ac', '1',
                '-y',
                temp_audio
            ], capture_output=True)

            # Convert to text
            recognizer = sr.Recognizer()
            with sr.AudioFile(temp_audio) as source:
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio, language=language)
                return text

        except subprocess.CalledProcessError as e:
            logging.error(f"FFmpeg error: {e.stderr.decode()}")
            raise ValueError("ไม่สามารถแปลงไฟล์เสียงได้")
        except sr.UnknownValueError:
            raise ValueError("ไม่สามารถแปลงเสียงเป็นข้อความได้")
        except Exception as e:
            logging.error(f"Error processing media: {str(e)}")
            raise
        finally:
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
