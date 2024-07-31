import os
import shutil
import subprocess
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes in the app
port = 5000

# Ensure the 'uploads' and 'results' directories exist
if not os.path.exists('uploads'):
    os.makedirs('uploads')

if not os.path.exists('results'):
    os.makedirs('results')


voice_folder = "assets/voice"
avatar_folder = "assets/avatar"

# Get list of images with multiple extensions
image_extensions = ('.jpeg', '.jpg', '.png')
voice_extensions = ('.mp3', '.wav')

@app.route('/doyentalker', methods=['POST'])
@cross_origin()



def doyentalker():
    data = request.form

    # Extract parameters from form data
    message = data.get('message')
    lang = data.get('lang')
    voice_name = data.get("voice_name")
    avatar_name = data.get("avatar_name")
    
        
    # Get the uploaded files
    user_audio_file = request.files.get('voice_name')
    user_avatar = request.files.get('avatar_name')
    
    if user_audio_file:
        voice = os.path.join('uploads', user_audio_file.filename)
        user_audio_file.save(voice)
    elif voice_name:
        voice = next((os.path.join(voice_folder, f) for f in os.listdir(voice_folder) if f.startswith(voice_name) and f.endswith(voice_extensions)), '')
    else:
        return jsonify({"status": "error", "message": "No audio provided."})
    

    if user_avatar:
        avatar_image = os.path.join('uploads', user_avatar.filename)
        user_avatar.save(avatar_image)
    elif avatar_name:
        avatar_image = next((os.path.join(avatar_folder, f) for f in os.listdir(avatar_folder) if f.startswith(avatar_name) and f.endswith(image_extensions)), '')
    else:
        return jsonify({"status": "error", "message": "No image provided."})
    
    # print("Response: ", data)
   
    # Execute your DoyenTalker logic here
    video_path = execute_doyentalker(message,voice, lang, avatar_image)
    
    final_vid_path = os.path.join('results',os.path.basename(video_path))
    
    if video_path:
        return jsonify({"status": "success", "message": "Video generation successful.", "video_url": f"{(final_vid_path)}"})
    else:
        return jsonify({"status": "error", "message": "Video generation failed."})


cors = CORS(app, origins="*")
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = 'local'

def execute_doyentalker(message, voice, lang, avatar_image):
    
    final_path = os.path.join('..', 'frontend', 'src', 'results')

    # Ensure the destination directory exists
    os.makedirs(final_path,exist_ok=True)

    # Build command with provided arguments
    command = [
        "python", "main.py",
        "--message", message,
        "--lang", lang,
        "--voice", voice,
        "--avatar_image", avatar_image,
        "--result_dir", final_path
    ]
    print("Command: ", command)
    
    try:
        subprocess.run(command, check=True, cwd=os.path.dirname(__file__))
        return final_path
    except subprocess.CalledProcessError as e:
        print(f"Error running DoyenTalker: {e}")
        return None


if __name__ == '__main__':
    app.run(port=port, debug=True)
