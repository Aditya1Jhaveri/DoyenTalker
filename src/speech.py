import os
import torch
from TTS.api import TTS
import time
from argparse import ArgumentParser

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

def speech(args):
    #  Create a unique path based on the current timestamp
    path_id = os.path.join("temp", str(int(time.time())))
    os.makedirs(path_id, exist_ok=True)
    
    # Function to read the content of the message file
    def read_message_from_file(file_path):
        with open(file_path, 'r') as file:
            return file.read()

    # Initialize variables
    message = None
    
    # Conditionally read the message file
    if args.message_file:
        message = read_message_from_file(args.message_file)
        
    speaker_wav = args.voice
    outfile = "output.wav"
    language = args.lang
    
    try:
        output_path = generate_speech(path_id, outfile,text=message, speaker_wav=speaker_wav, language=language)
        print(f"Speech saved to {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    parser = ArgumentParser()
    
    parser.add_argument("--message_file", type=str, help="path to the file containing the speech message")
    parser.add_argument("--voice", type=str, default='./assets/voice/ab_voice.mp3', help="path to speaker voice file")
    parser.add_argument("--lang", type=str, default='en', help="select the language for speaker voice option are (en - English , es - Spanish , fr - French , de - German , it - Italian , pt - Portuguese , pl - Polish , tr - Turkish , ru - Russian , nl - Dutch , cs - Czech , ar - Araic , zh-cn - Chinese (Simplified) , hu - Hungarian , ko - Korean , ja - Japanese , hi - Hindi)")
   
    args = parser.parse_args()

    speech(args)
   
