import os
import subprocess
import sys
import logging
import requests
from pathlib import Path

class FFmpegSetup:
    @staticmethod
    def download_ffmpeg():
        """Download and setup ffmpeg for Windows"""
        try:
            ffmpeg_dir = Path("ffmpeg")
            ffmpeg_dir.mkdir(exist_ok=True)
            
            # Download ffmpeg
            url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            zip_path = ffmpeg_dir / "ffmpeg.zip"
            
            print("กำลังดาวน์โหลด FFmpeg...")
            response = requests.get(url, stream=True)
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Extract FFmpeg
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(ffmpeg_dir)
            
            # Add to PATH
            ffmpeg_bin = str(ffmpeg_dir / "ffmpeg-master-latest-win64-gpl" / "bin")
            if ffmpeg_bin not in os.environ['PATH']:
                os.environ['PATH'] = ffmpeg_bin + os.pathsep + os.environ['PATH']
            
            # Cleanup
            zip_path.unlink()
            return True
            
        except Exception as e:
            logging.error(f"Error downloading FFmpeg: {str(e)}")
            return False

    @staticmethod
    def check_ffmpeg():
        """Check if ffmpeg is installed and accessible"""
        try:
            subprocess.run(['ffmpeg', '-version'], capture_output=True)
            return True
        except FileNotFoundError:
            try:
                if sys.platform == 'win32':
                    return FFmpegSetup.download_ffmpeg()
                else:
                    logging.error("กรุณาติดตั้ง FFmpeg ด้วยคำสั่ง:")
                    if sys.platform == 'darwin':  # Mac
                        logging.error("brew install ffmpeg")
                    else:  # Linux
                        logging.error("sudo apt-get install ffmpeg")
                    return False
            except Exception as e:
                logging.error(f"ไม่สามารถติดตั้ง FFmpeg ได้: {str(e)}")
                return False
