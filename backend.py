from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import subprocess

app = Flask(__name__)
port = 5000

@app.route('/doyentalker', methods=['POST'])
def doyentalker():
    data = request.json

    # Extract parameters from JSON request
    message = data.get('message')
    voice = save_uploaded_file(data.get('voice'), 'voice')
    lang = data.get('lang')
    source_image = save_uploaded_file(data.get('source_image'), 'image')
    expression_scale = data.get('expression_scale')
    enhancer = data.get('enhancer')
    background_enhancer = data.get('background_enhancer')
    still = data.get('still')
    preprocess = data.get('preprocess')

    # Execute your DoyenTalker logic here
    result = execute_doyentalker(message, voice, lang, source_image, expression_scale, enhancer, background_enhancer, still, preprocess)

    return jsonify(result)

def save_uploaded_file(uploaded_file, file_type):
    if uploaded_file:
        filename = secure_filename(uploaded_file.filename)
        file_path = os.path.join('./results', filename)  # Adjust save path
        uploaded_file.save(file_path)
        return file_path
    else:
        return None

def execute_doyentalker(message, voice, lang, source_image, expression_scale, enhancer, background_enhancer, still, preprocess):
    # Implement your DoyenTalker execution logic here
    # This could involve calling subprocesses, executing scripts, etc.
    # Example:
    command = [
        "python", "main.py",
        "--message", message,
        "--voice", voice,
        "--lang", lang,
        "--source_image", source_image,
        "--expression_scale", expression_scale,
        "--enhancer", enhancer,
        "--background_enhancer", background_enhancer,
        "--still", still,
        "--preprocess", preprocess,
    ]
    subprocess.run(command, check=True)  # Example subprocess execution

    # Example response
    return {"status": "success", "video_path": "/path/to/generated/video.mp4"}

if __name__ == '__main__':
    app.run(port=port)
