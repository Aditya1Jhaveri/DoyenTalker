
import os
import torch
from TTS.api import TTS
import time
# import humanize
import datetime as dt

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"

# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

def generate_speech(path_id, outfile, text, speaker_wav=None, language="en"):
    # Generate the full path for the output file
    output_path = os.path.join(path_id, outfile)
    
    # Generate speech and save to a file
    tts.tts_to_file(text=text, file_path=output_path, speaker_wav=speaker_wav, language=language)
    
    return output_path

def main():
    # Create a unique path based on the current timestamp
    path_id = os.path.join("results", str(int(time.time())))
    os.makedirs(path_id, exist_ok=True)
    
    print(f"path_id: {path_id} path: {os.path.abspath(path_id)}")
    
    message = """Reading offers numerous benefits beyond simple entertainment, encompassing cognitive, emotional, and social dimensions. 
    It acts as a mental workout, sharpening critical thinking, concentration, and analytical skills while expanding vocabulary and knowledge. 
    Additionally, it fosters empathy and emotional intelligence by allowing readers to inhabit different perspectives and experiences. 
    Reading is a gateway to diverse cultures, histories, and ideas, promoting open-mindedness and cultural understanding. 
    Moreover, it provides relaxation and stress reduction, offering an escape from daily pressures. 
    Furthermore, it can enhance communication skills and creativity, sparking imagination and innovation. 
    Ultimately, reading is a lifelong pursuit that enriches individuals’ lives intellectually, emotionally, and socially."""

    speaker_wav = "/content/drive/MyDrive/Y2meta.app - Trump Makes CPAC Crowd Laugh Doing Mean Impression Of Biden Trying To Get Off Stage (256 kbps).mp3"
    outfile = "output.wav"
    language = "en"
    
    try:
        output_path = generate_speech(path_id, outfile, message, speaker_wav=speaker_wav, language=language)
        print(f"Speech saved to {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
   
    main()
   
