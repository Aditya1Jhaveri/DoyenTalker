import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import os
import base64

# # Import your existing functions and modules
# from src.speech import generate_speech
# from src.utils.preprocess import CropAndExtract
# from src.audio2coeff import Audio2Coeff
# from src.facerender.animate import AnimateFromCoeff
# from src.generate_audio_batch import get_data
# from src.generate_facerender_batch import get_facerender_data
# from src.utils.init_path import init_path
# import shutil
# import time
# import torch
# import datetime as dt
# import humanize
# from argparse import Namespace
# from moviepy.editor import concatenate_videoclips, VideoFileClip


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes in the app
port = 5000

# Ensure the 'uploads' directories exist
os.makedirs('uploads', exist_ok=True)

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
        return jsonify({"status": "error", "message": "No audio provided."}), 400

    if user_avatar:
        avatar_image = os.path.join('uploads', user_avatar.filename)
        user_avatar.save(avatar_image)
    elif avatar_name:
        avatar_image = next((os.path.join(avatar_folder, f) for f in os.listdir(avatar_folder) if f.startswith(avatar_name) and f.endswith(image_extensions)), '')
    else:
        return jsonify({"status": "error", "message": "No image provided."}), 400
    
    ## Executing the logic here  
    video_path = execute_doyentalker(message,lang,voice, avatar_image)
    
    # Find the generated .mp4 file
    generated_video = next((os.path.join(video_path, f) for f in os.listdir(video_path) if f.endswith('.mp4')), None)
    
     # Read the video file and encode it as base64
    with open(generated_video, "rb") as video_file:
        encoded_string = base64.b64encode(video_file.read()).decode('utf-8')

   
    return jsonify({"status": "success", "message": "Video generation successful.", "video_url": f"{encoded_string}"})
    

cors = CORS(app, origins="*")

def execute_doyentalker(message,lang, voice,avatar_image):
    final_path = os.path.join('results')

    # Ensure the destination directory exists
    os.makedirs(final_path, exist_ok=True)

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



# def split_text(text, max_words=100):
#     # Split the text into chunks of max_words each
#     words = text.split()
#     return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]


# def execute_doyentalker(input_text, lang, voice, image):
    
#     args = Namespace(
#         message_file=input_text,
#         lang=lang,
#         voice=voice,
#         avatar_image=image,
#         expression_scale=1.5,
#         preprocess="full",
#         still=True,
#         enhancer=None,
#         background_enhancer=None,
#         checkpoint_dir='./checkpoints',
#         pose_style=0,
#         batch_size=2,
#         size=256,
#         input_yaw=None,
#         input_pitch=None,
#         input_roll=None,
#         ref_eyeblink=None,
#         ref_pose=None,
#         cpu=False, 
#         face3dvis=False,
#         old_version=False
#     )

#     if torch.cuda.is_available() and not args.cpu:
#         args.device = "cuda"
#     else:
#         args.device = "cpu"

#     return interface(args)  # Call the interface function to generate the video and return its path

# def interface(args):
#     tstart = time.time()

#     input_voice = args.voice
#     input_lang = args.lang
#     text_message = args.message_file

#     # Create unique directories for different steps
#     path = os.path.join("results", str(int(time.time())))
#     os.makedirs(path, exist_ok=True)

#     # Generate audio for chunks of text
#     audio_files = []
#     text_chunks = split_text(text_message)  # Function to split text into chunks
    
#     tspeech_start = time.time()  # Start timing speech generation

#     for i, text in enumerate(text_chunks):
#         audio_file = f"output_part_{i + 1}.wav"
#         audio_path = os.path.join(path, audio_file)
#         try:
#             generate_speech(path, audio_file, text, input_voice, input_lang)
#             audio_files.append(audio_path)
#         except Exception as e:
#             print(f"An error occurred while generating audio for text {i + 1}: {e}")

#     tspeech_end = time.time()  
#     tspeech = tspeech_end - tspeech_start

#     video_files = []
    
#     # Process image and generate videos for each audio segment
#     pic_path = args.avatar_image
#     save_dir = path
#     pose_style = args.pose_style
#     device = args.device
#     batch_size = args.batch_size
#     input_yaw_list = args.input_yaw
#     input_pitch_list = args.input_pitch
#     input_roll_list = args.input_roll
#     ref_eyeblink = args.ref_eyeblink
#     ref_pose = args.ref_pose

#     current_root_path = os.path.split(__file__)[0]

#     doyentalker_paths = init_path(args.checkpoint_dir, os.path.join(current_root_path, 'src/config'), args.size, args.old_version, args.preprocess)

#     # Init models
#     preprocess_model = CropAndExtract(doyentalker_paths, device)
#     audio_to_coeff = Audio2Coeff(doyentalker_paths, device)
#     animate_from_coeff = AnimateFromCoeff(doyentalker_paths, device)

#     # Crop image and extract 3dmm from image
#     first_frame_dir = os.path.join(save_dir, 'first_frame_dir')
#     os.makedirs(first_frame_dir, exist_ok=True)
#     print('3DMM Extraction for source image')
#     timage_start = time.time()
    
#     first_coeff_path, crop_pic_path, crop_info = preprocess_model.generate(pic_path, first_frame_dir, args.preprocess, avatar_image_flag=True, pic_size=args.size)
    
#     timage_end = time.time()
#     timage = timage_end - timage_start
    
#     if first_coeff_path is None:
#         print("Can't get the coeffs of the input")
#         return None

#     if ref_eyeblink is not None:
#         ref_eyeblink_videoname = os.path.splitext(os.path.split(ref_eyeblink)[-1])[0]
#         ref_eyeblink_frame_dir = os.path.join(save_dir, ref_eyeblink_videoname)
#         os.makedirs(ref_eyeblink_frame_dir, exist_ok=True)
#         print('3DMM Extraction for the reference video providing eye blinking')
#         ref_eyeblink_coeff_path, _, _ = preprocess_model.generate(ref_eyeblink, ref_eyeblink_frame_dir, args.preprocess, avatar_image_flag=False)
#     else:
#         ref_eyeblink_coeff_path = None

#     if ref_pose is not None:
#         if ref_pose == ref_eyeblink:
#             ref_pose_coeff_path = ref_eyeblink_coeff_path
#         else:
#             ref_pose_videoname = os.path.splitext(os.path.split(ref_pose)[-1])[0]
#             ref_pose_frame_dir = os.path.join(save_dir, ref_pose_videoname)
#             os.makedirs(ref_pose_frame_dir, exist_ok=True)
#             print('3DMM Extraction for the reference video providing pose')
#             ref_pose_coeff_path, _, _ = preprocess_model.generate(ref_pose, ref_pose_frame_dir, args.preprocess, avatar_image_flag=False)
#     else:
#         ref_pose_coeff_path = None

#     tanimate_start = time.time()
#     # Process each audio file
#     for i, audio_path in enumerate(audio_files):
#         # Generate video for the current audio file
#         batch = get_data(first_coeff_path, audio_path, device, ref_eyeblink_coeff_path, still=args.still)
#         coeff_path = audio_to_coeff.generate(batch, save_dir, pose_style, ref_pose_coeff_path)
        
#         # 3dface render
#         if args.face3dvis:
#             from src.face3d.visualize import gen_composed_video
#             gen_composed_video(args, device, first_coeff_path, coeff_path, audio_path, os.path.join(save_dir, f'3dface_part_{i + 1}.mp4'))
        
#         # coeff2video

        
#         data = get_facerender_data(coeff_path, crop_pic_path, first_coeff_path, audio_path,
#                                    batch_size, input_yaw_list, input_pitch_list, input_roll_list,
#                                    expression_scale=args.expression_scale, still_mode=args.still, preprocess=args.preprocess, size=args.size)

#         result = animate_from_coeff.generate(data, save_dir, pic_path, crop_info,
#                                              enhancer=args.enhancer, background_enhancer=args.background_enhancer, preprocess=args.preprocess, img_size=args.size)
        
#         # Save video path
#         video_file = os.path.join(save_dir, f'generated_video_part_{i + 1}.mp4')
#         shutil.move(result, video_file)
#         video_files.append(video_file)
#         print(f'Video for part {i + 1} is named:', video_file)
        
#         tanimate_end = time.time()
#         tanimate = tanimate_end - tanimate_start
        
#     # Combine all video files
    
#     tcombine_video_start = time.time()  
#     combined_video_path = os.path.join(save_dir, 'combined_generated_video.mp4')
#     clips = [VideoFileClip(v) for v in video_files]
    
    
#     final_clip = concatenate_videoclips(clips, method="compose")
#     final_clip.write_videofile(combined_video_path, codec="libx264")
    
#     tcombine_video_end = time.time()  
#     t_combine_video = tcombine_video_end - tcombine_video_start

#     print("done")
#     print("Overall timing")
#     print("--------------")
#     print("generating speech:", humanize.naturaldelta(dt.timedelta(seconds=tspeech)))
#     print("generating avatar image:", humanize.naturaldelta(dt.timedelta(seconds=timage)))
#     print("animating face:", humanize.naturaldelta(dt.timedelta(seconds=tanimate)))
#     print("Combined video:", humanize.naturaldelta(dt.timedelta(seconds=t_combine_video)))
#     print("total time:", humanize.naturaldelta(dt.timedelta(seconds=int(time.time() - tstart))))

#     return combined_video_path
