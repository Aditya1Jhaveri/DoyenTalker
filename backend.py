import os
import subprocess
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import tempfile

app = Flask(__name__)
port = 5000

@app.route('/doyentalker', methods=['POST'])
def doyentalker():
    data = request.json

    # Extract parameters from JSON request
    message = data.get('message')
    lang = data.get('lang')
    expression_scale = data.get('expression_scale')
    enhancer = data.get('enhancer')
    background_enhancer = data.get('background_enhancer')
    still = data.get('still')
    preprocess = data.get('preprocess')

   
    voice = "./example/test_audio.mp3"
    source_image = "./example/test_img.jpeg"


    # Execute your DoyenTalker logic here
    result = execute_doyentalker(message, voice, lang, source_image, expression_scale, enhancer, background_enhancer, still, preprocess)

    return jsonify(result)


def execute_doyentalker(message, voice, lang, source_image, expression_scale, enhancer, background_enhancer, still, preprocess):
    # Build command with provided arguments
    command = [
        "python", "main.py",
        "--message", message,
        "--lang", lang,
        "--voice", voice,
        "--source_image", source_image,
        "--expression_scale", str(expression_scale),
        "--enhancer", str(enhancer),
        "--background_enhancer", str(background_enhancer),
        "--still", str(still),
        "--preprocess", preprocess,
    ]
    
    print("Command: ", command)
    
    # Run subprocess command
    try:
        subprocess.run(command, check=True, cwd=os.path.dirname(__file__))  # Set cwd to current script directory
        return {"status": "success", "message": "Video generation successful."}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Error running DoyenTalker: {e}"}

if __name__ == '__main__':
    app.run(port=port)
