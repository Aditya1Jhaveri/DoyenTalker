import os
import subprocess
from flask import Flask, request, jsonify


app = Flask(__name__)
port = 5000

@app.route('/doyentalker', methods=['POST'])
def doyentalker():
    data = request.json

    # Extract parameters from JSON request
    message = data.get('message')
    lang = data.get('lang')
        
    voice = "assets/voice/ab_voice.mp3"
    avatar_image = "assets/avatar/male9.jpeg"
    
    # voice_folder = "assets/voice"
    # avatar_folder = "assets/avatar"

    # # Get list of images with multiple extensions
    # image_extensions = ('.jpeg', '.jpg', '.png')
    # voice_extensions = ('.mp3', '.wav')
    
    # avatar_image = next((os.path.join(avatar_folder, f) for f in os.listdir(avatar_folder) if f.startswith(avatar_image) and f.endswith(image_extensions)), '')
        
    # voice = next((os.path.join(voice_folder, f) for f in os.listdir(voice_folder) if f.startswith(voice) and f.endswith(voice_extensions)), '')


    # Execute your DoyenTalker logic here
    result = execute_doyentalker(message, voice, lang, avatar_image)

    return jsonify(result)


def execute_doyentalker(message, voice, lang, avatar_image):
    # Build command with provided arguments
    command = [
        "python", "main.py",
        "--message", message,
        "--lang", lang,
        "--voice", voice,
        "--avatar_image", avatar_image,
    ]
    
    print("Command: ", command)
    
    # Run subprocess command
    try:
        subprocess.run(command, check=True, cwd=os.path.dirname(__file__))  # Set cwd to current script directory
        return {"status": "success", "message": "Video generation successful."}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Error running DoyenTalker: {e}"}

if __name__ == '__main__':
    app.run(port=port,debug=True)
