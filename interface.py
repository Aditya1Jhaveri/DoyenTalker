import os
import shutil
import time
import torch
import datetime as dt
import humanize
from argparse import Namespace
from moviepy.editor import concatenate_videoclips, VideoFileClip
import gradio as gr

# Import your existing functions and modules
from src.speech import generate_speech
from src.utils.preprocess import CropAndExtract
from src.audio2coeff import Audio2Coeff
from src.facerender.animate import AnimateFromCoeff
from src.generate_audio_batch import get_data
from src.generate_facerender_batch import get_facerender_data
from src.utils.init_path import init_path

voice_folder = "assets/voice"
avatar_folder = "assets/avatar"

# Get list of images with multiple extensions
image_extensions = ('.jpeg', '.jpg', '.png')
voice_extensions = ('.mp3', '.wav')

def split_text(text, max_words=100):
    # Split the text into chunks of max_words each
    words = text.split()
    return [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]

def generate_video_interface(input_text, lang, voice, image, user_audio, gfpgan):
    # Handle user audio
    voice_file = None
    if user_audio:
        voice_file = user_audio
    else:
        voice_file = next((os.path.join(voice_folder, f) for f in os.listdir(voice_folder) if f.startswith(voice) and f.endswith(voice_extensions)), '')

    image_file = next((os.path.join(avatar_folder, f) for f in os.listdir(avatar_folder) if f.startswith(image) and f.endswith(image_extensions)), '')

    # enhancer = None
    # if gfpgan:
    #     enhancer = "gfpgan"
    # else:
    #     enhancer = "RestoreFormer"

    args = Namespace(
        message_file=input_text,
        lang=lang,
        voice=voice_file,
        avatar_image=image_file,
        expression_scale=1.5,
        preprocess="full",
        still=True,
        enhancer=None,
        background_enhancer=None,
        checkpoint_dir='./checkpoints',
        pose_style=0,
        batch_size=2,
        size=256,
        input_yaw=None,
        input_pitch=None,
        input_roll=None,
        ref_eyeblink=None,
        ref_pose=None,
        cpu=False, 
        face3dvis=False,
        old_version=False
    )

    if torch.cuda.is_available() and not args.cpu:
        args.device = "cuda"
    else:
        args.device = "cpu"

    return interface(args)  # Call the interface function to generate the video and return its path

def interface(args):
    tstart = time.time()

    input_voice = args.voice
    input_lang = args.lang
    text_message = args.message_file

    # Create unique directories for different steps
    path = os.path.join("results", str(int(time.time())))
    os.makedirs(path, exist_ok=True)

    # Generate audio for chunks of text
    audio_files = []
    text_chunks = split_text(text_message)  # Function to split text into chunks
    
    tspeech_start = time.time()  # Start timing speech generation

    for i, text in enumerate(text_chunks):
        audio_file = f"output_part_{i + 1}.wav"
        audio_path = os.path.join(path, audio_file)
        try:
            generate_speech(path, audio_file, text, input_voice, input_lang)
            audio_files.append(audio_path)
        except Exception as e:
            print(f"An error occurred while generating audio for text {i + 1}: {e}")

    tspeech_end = time.time()  
    tspeech = tspeech_end - tspeech_start

    video_files = []
    
    # Process image and generate videos for each audio segment
    pic_path = args.avatar_image
    save_dir = path
    pose_style = args.pose_style
    device = args.device
    batch_size = args.batch_size
    input_yaw_list = args.input_yaw
    input_pitch_list = args.input_pitch
    input_roll_list = args.input_roll
    ref_eyeblink = args.ref_eyeblink
    ref_pose = args.ref_pose

    current_root_path = os.path.split(__file__)[0]

    doyentalker_paths = init_path(args.checkpoint_dir, os.path.join(current_root_path, 'src/config'), args.size, args.old_version, args.preprocess)

    # Init models
    preprocess_model = CropAndExtract(doyentalker_paths, device)
    audio_to_coeff = Audio2Coeff(doyentalker_paths, device)
    animate_from_coeff = AnimateFromCoeff(doyentalker_paths, device)

    # Crop image and extract 3dmm from image
    first_frame_dir = os.path.join(save_dir, 'first_frame_dir')
    os.makedirs(first_frame_dir, exist_ok=True)
    print('3DMM Extraction for source image')
    timage_start = time.time()
    
    first_coeff_path, crop_pic_path, crop_info = preprocess_model.generate(pic_path, first_frame_dir, args.preprocess, avatar_image_flag=True, pic_size=args.size)
    
    timage_end = time.time()
    timage = timage_end - timage_start
    
    if first_coeff_path is None:
        print("Can't get the coeffs of the input")
        return None

    if ref_eyeblink is not None:
        ref_eyeblink_videoname = os.path.splitext(os.path.split(ref_eyeblink)[-1])[0]
        ref_eyeblink_frame_dir = os.path.join(save_dir, ref_eyeblink_videoname)
        os.makedirs(ref_eyeblink_frame_dir, exist_ok=True)
        print('3DMM Extraction for the reference video providing eye blinking')
        ref_eyeblink_coeff_path, _, _ = preprocess_model.generate(ref_eyeblink, ref_eyeblink_frame_dir, args.preprocess, avatar_image_flag=False)
    else:
        ref_eyeblink_coeff_path = None

    if ref_pose is not None:
        if ref_pose == ref_eyeblink:
            ref_pose_coeff_path = ref_eyeblink_coeff_path
        else:
            ref_pose_videoname = os.path.splitext(os.path.split(ref_pose)[-1])[0]
            ref_pose_frame_dir = os.path.join(save_dir, ref_pose_videoname)
            os.makedirs(ref_pose_frame_dir, exist_ok=True)
            print('3DMM Extraction for the reference video providing pose')
            ref_pose_coeff_path, _, _ = preprocess_model.generate(ref_pose, ref_pose_frame_dir, args.preprocess, avatar_image_flag=False)
    else:
        ref_pose_coeff_path = None


    # Process each audio file
    for i, audio_path in enumerate(audio_files):
        # Generate video for the current audio file
        batch = get_data(first_coeff_path, audio_path, device, ref_eyeblink_coeff_path, still=args.still)
        coeff_path = audio_to_coeff.generate(batch, save_dir, pose_style, ref_pose_coeff_path)
        
        # 3dface render
        if args.face3dvis:
            from src.face3d.visualize import gen_composed_video
            gen_composed_video(args, device, first_coeff_path, coeff_path, audio_path, os.path.join(save_dir, f'3dface_part_{i + 1}.mp4'))
        
        # coeff2video
        tanimate_start = time.time()
        
        data = get_facerender_data(coeff_path, crop_pic_path, first_coeff_path, audio_path,
                                   batch_size, input_yaw_list, input_pitch_list, input_roll_list,
                                   expression_scale=args.expression_scale, still_mode=args.still, preprocess=args.preprocess, size=args.size)

        result = animate_from_coeff.generate(data, save_dir, pic_path, crop_info,
                                             enhancer=args.enhancer, background_enhancer=args.background_enhancer, preprocess=args.preprocess, img_size=args.size)
        tanimate_end = time.time()
        tanimate = tanimate_end - tanimate_start
        
        # Save video path
        video_file = os.path.join(save_dir, f'generated_video_part_{i + 1}.mp4')
        shutil.move(result, video_file)
        video_files.append(video_file)
        print(f'Video for part {i + 1} is named:', video_file)
        
    
    # Combine all video files
    
    tcombine_video_start = time.time()  
    combined_video_path = os.path.join(save_dir, 'combined_generated_video.mp4')
    clips = [VideoFileClip(v) for v in video_files]
    
    
    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(combined_video_path, codec="libx264")
    
    tcombine_video_end = time.time()  
    t_combine_video = tcombine_video_end - tcombine_video_start

    print("done")
    print("Overall timing")
    print("--------------")
    print("generating speech:", humanize.naturaldelta(dt.timedelta(seconds=tspeech)))
    print("generating avatar image:", humanize.naturaldelta(dt.timedelta(seconds=timage)))
    print("animating face:", humanize.naturaldelta(dt.timedelta(seconds=tanimate)))
    print("Combined video:", humanize.naturaldelta(dt.timedelta(seconds=t_combine_video)))
    print("total time:", humanize.naturaldelta(dt.timedelta(seconds=int(time.time() - tstart))))

    return combined_video_path

def update_image_and_voice(voice, image):
    image_file = next((os.path.join(avatar_folder, f) for f in os.listdir(avatar_folder) if f.startswith(image) and f.endswith(image_extensions)), '')
    voice_file = next((os.path.join(voice_folder, f) for f in os.listdir(voice_folder) if f.startswith(voice) and f.endswith(voice_extensions)), '')
    
    if not os.path.exists(voice_file):
        raise ValueError(f"Voice file {voice_file} does not exist.")
    if not os.path.exists(image_file):
        raise ValueError(f"Image file {image_file} does not exist.")
    
    return gr.update(value=image_file), gr.update(value=voice_file)

# Define available voices and images
available_voices = [f.split('.')[0] for f in os.listdir(voice_folder) if f.endswith(voice_extensions)]
available_images = [f.split('.')[0] for f in os.listdir(avatar_folder) if f.endswith(image_extensions)]

def toggle_audio_input(radio_choice):
        if radio_choice == "mic":
            return gr.update(visible=True), gr.update(visible=False), gr.update(visible=True)
        else:
            return gr.update(visible=False), gr.update(visible=True), gr.update(visible=False)

speech = (
    "Ladies and gentlemen,\n\n"
    "Education is the cornerstone of our society, shaping the minds and futures of our youth. It is not merely about acquiring knowledge from textbooks, "
    "but also about developing critical thinking, creativity, and the ability to adapt to an ever-changing world. Every child deserves access to quality education, "
    "as it lays the foundation for personal growth, career success, and civic responsibility.\n\n"
    "Investing in education means investing in the future. It empowers individuals to break the cycle of poverty, fosters innovation, and drives economic development. "
    "In today's digital age, it is crucial to integrate technology into the learning process, making education more accessible and engaging for all.\n\n"
    "Teachers play a pivotal role in this journey. Their dedication and passion inspire students to reach their full potential. Therefore, we must support and value our educators, "
    "providing them with the resources and training they need to thrive.\n\n"
    "Let us work together to create an inclusive and equitable education system that nurtures the talents of every student, ensuring a brighter, more prosperous future for all.\n\n"
    "Thank you."
)

# Define the Gradio interface using Blocks
with gr.Blocks() as iface:
    gr.Markdown("## Generate Video with Voice Cloning and Avatars")

    text_input = gr.Textbox(
        lines=2,
        placeholder="Enter the text you want to generate speech for",
        label="Input Text",
        info="Words Limit = 180 words for better audio"
    )
    lang_choice = gr.Radio(
        label="Language",
        choices=['en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr', 'ru', 'nl', 'cs', 'ar', 'zh-cn', 'hu', 'ko', 'ja', 'hi'],
        info="en - English, es - Spanish, fr - French, de - German, it - Italian, pt - Portuguese, pl - Polish, tr - Turkish, ru - Russian, nl - Dutch, cs - Czech, ar - Arabic, zh-cn - Chinese (Simplified), hu - Hungarian, ko - Korean, ja - Japanese, hi - Hindi",
        value="en"
    )
    avatar_dropdown = gr.Dropdown(
        label="Select Avatar",
        choices=available_images,
        value="male1",
        interactive=True
    )
    radio_choice = gr.Radio(
        ["mic", "predefined voice"],
        value="predefined voice",
        label="How would you like to choose the voice?",
    )
    user_audio = gr.Audio(
        label="Customize Voice (Read below paragraph for clear voice cloning)",
        sources=["microphone"],
        type="filepath",
        visible=False
    )
    voice_dropdown = gr.Dropdown(
        label="Select Voice",
        choices=available_voices,
        value="ab_voice",
        interactive=True,
        visible=True
    )
    markdown = gr.Markdown(speech, visible=False)
    # gfpgan= gr.Checkbox(label="Enhancer for face", value=True),
    
    # Update components based on radio choice
    radio_choice.change(toggle_audio_input, inputs=[radio_choice], outputs=[user_audio, voice_dropdown, markdown])
    
    video_output = gr.Video(format="mp4")
    
    # Define the Interface within Blocks
    gr.Interface(
        fn=generate_video_interface,
        inputs=[text_input, lang_choice, voice_dropdown, avatar_dropdown, user_audio],
        outputs=video_output
    )

iface.launch(debug=True)
