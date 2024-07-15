import gradio as gr
import shutil
import torch
import time
import os
import datetime as dt
import humanize
from argparse import Namespace

# Import your existing functions and modules
from src.speech import generate_speech
from src.utils.preprocess import CropAndExtract
from src.test_audio2coeff import Audio2Coeff
from src.facerender.animate import AnimateFromCoeff
from src.generate_batch import get_data
from src.generate_facerender_batch import get_facerender_data
from src.utils.init_path import init_path

def generate_video_interface(input_text, lang, voice, image,gfpgan):
    voice_folder = "example/voice"
    avatar_folder = "example/avatar"
    
    voice_file = os.path.join(voice_folder, f"{voice}.mp3")
    image_file = os.path.join(avatar_folder, f"{image}.jpeg")
    
    args = Namespace(
        message_file=input_text,
        lang=lang,
        voice=voice_file,
        source_image=image_file,
        expression_scale=1.5,
        preprocess="full",
        still=False,
        enhancer=gfpgan,
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

    path = os.path.join("results", str(int(time.time())))
    path_id = path
    print("path_id:", path_id, "path:", path)
    os.makedirs(path, exist_ok=True)

    tts_output = "output.wav"

    print("-----------------------------------------")
    print("generating speech")
    tspeech_start = time.time()
    generate_speech(path_id, tts_output, text_message, input_voice, input_lang)
    tspeech_end = time.time()
    tspeech = tspeech_end - tspeech_start
    print("\ngenerating speech:", tts_output)

    tts_audio = os.path.join(path, "output.wav")

    pic_path = args.source_image
    audio_path = tts_audio
    save_dir = path
    os.makedirs(save_dir, exist_ok=True)
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
    first_coeff_path, crop_pic_path, crop_info = preprocess_model.generate(pic_path, first_frame_dir, args.preprocess, source_image_flag=True, pic_size=args.size)
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
        ref_eyeblink_coeff_path, _, _ = preprocess_model.generate(ref_eyeblink, ref_eyeblink_frame_dir, args.preprocess, source_image_flag=False)
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
            ref_pose_coeff_path, _, _ = preprocess_model.generate(ref_pose, ref_pose_frame_dir, args.preprocess, source_image_flag=False)
    else:
        ref_pose_coeff_path = None

    # audio2coeff
    batch = get_data(first_coeff_path, audio_path, device, ref_eyeblink_coeff_path, still=args.still)
    coeff_path = audio_to_coeff.generate(batch, save_dir, pose_style, ref_pose_coeff_path)

    # 3dface render
    if args.face3dvis:
        from src.face3d.visualize import gen_composed_video
        gen_composed_video(args, device, first_coeff_path, coeff_path, audio_path, os.path.join(save_dir, '3dface.mp4'))

    # coeff2video
    tanimate_start = time.time()
    data = get_facerender_data(coeff_path, crop_pic_path, first_coeff_path, audio_path,
                               batch_size, input_yaw_list, input_pitch_list, input_roll_list,
                               expression_scale=args.expression_scale, still_mode=args.still, preprocess=args.preprocess, size=args.size)

    result = animate_from_coeff.generate(data, save_dir, pic_path, crop_info,
                                         enhancer=args.enhancer, background_enhancer=args.background_enhancer, preprocess=args.preprocess, img_size=args.size)
    tanimate_end = time.time()
    tanimate = tanimate_end - tanimate_start

    generated_video_path = os.path.join(save_dir, 'generated_video.mp4')
    shutil.move(result, generated_video_path)
    print('The generated video is named:', generated_video_path)

    print("done")
    print("Overall timing")
    print("--------------")
    print("generating speech:", humanize.naturaldelta(dt.timedelta(seconds=tspeech)))
    print("generating avatar image:", humanize.naturaldelta(dt.timedelta(seconds=timage)))
    print("animating face:", humanize.naturaldelta(dt.timedelta(seconds=tanimate)))
    print("total time:", humanize.naturaldelta(dt.timedelta(seconds=int(time.time() - tstart))))

    return generated_video_path

def update_image_and_voice(voice, image):
    voice_folder = "example/voice"
    avatar_folder = "example/avatar"
    
    voice_file = os.path.join(voice_folder, f"{voice}.mp3")
    image_file = os.path.join(avatar_folder, f"{image}.jpeg")
    
    if not os.path.exists(voice_file):
        raise ValueError(f"Voice file {voice_file} does not exist.")
    if not os.path.exists(image_file):
        raise ValueError(f"Image file {image_file} does not exist.")
    
    return gr.update(value=image_file), gr.update(value=voice_file)

# Define available voices and images
available_voices = ["ab_voice", "modi_voice", "srk_voice", "trump_voice"]
available_images = ["male1", "male2", "male3", "male4"]



# Create Gradio interface
iface = gr.Interface(
    fn=generate_video_interface,
    inputs=[
        gr.Textbox(placeholder="Enter text to convert to speech", label="Input the text", max_lines=3),
        gr.Radio(label="Language", choices=["en", "fr-fr", "pt-br", "zh-CN", "de", "es", "hi"], value="en"),
        gr.Dropdown(label="Select Voice", choices=available_voices, value="ab_voice", interactive=True),
        gr.Dropdown(label="Select Image", choices=available_images, value="male1", interactive=True),
        gr.checkbox(label="Enhancer for face", value="gfpgan"),
    ],
    outputs=[gr.Video(format="mp4")],
    title="DoyenTalker",
    description="Generate a video with DoyenTalker based on provided inputs.",

)

iface.launch(debug=True)
