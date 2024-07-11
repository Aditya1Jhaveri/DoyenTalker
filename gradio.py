import gradio as gr
import shutil
import torch
import time
import os, sys
from argparse import Namespace

from src.speech import generate_speech
from src.utils.preprocess import CropAndExtract
from src.test_audio2coeff import Audio2Coeff  
from src.facerender.animate import AnimateFromCoeff
from src.generate_batch import get_data
from src.generate_facerender_batch import get_facerender_data
from src.utils.init_path import init_path

def main(args):

    # Initialize variables
    message = args.message

    input_voice = args.voice
    input_lang = args.lang

    path = os.path.join("results", str(int(time.time())))
    path_id = path
    print("path_id:", path_id, "path:", path)
    os.makedirs(path, exist_ok=True)
 
    tts_output = "output.wav"
    
    print("-----------------------------------------")
    print("generating speech")
    generate_speech(path_id, tts_output, message, input_voice, input_lang)
    print("\ngenerating speech:", tts_output)
    
    tts_audio = os.path.join(path, "output.wav")

    pic_path = args.source_image
    audio_path = tts_output
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

    current_root_path = os.path.split(sys.argv[0])[0]

    doyentalker_paths = init_path(args.checkpoint_dir, os.path.join(current_root_path, 'src/config'), args.size, args.old_version, args.preprocess)

    # init model
    preprocess_model = CropAndExtract(doyentalker_paths, device)

    audio_to_coeff = Audio2Coeff(doyentalker_paths, device)
    
    animate_from_coeff = AnimateFromCoeff(doyentalker_paths, device)

    # crop image and extract 3dmm from image
    first_frame_dir = os.path.join(save_dir, 'first_frame_dir')
    os.makedirs(first_frame_dir, exist_ok=True)
    print('3DMM Extraction for source image')
    first_coeff_path, crop_pic_path, crop_info = preprocess_model.generate(pic_path, first_frame_dir, args.preprocess, source_image_flag=True, pic_size=args.size)
    if first_coeff_path is None:
        print("Can't get the coeffs of the input")
        return "Error: Can't get the coeffs of the input"

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

    # audio2ceoff
    batch = get_data(first_coeff_path, audio_path, device, ref_eyeblink_coeff_path, still=args.still)
    coeff_path = audio_to_coeff.generate(batch, save_dir, pose_style, ref_pose_coeff_path)

    # 3dface render
    if args.face3dvis:
        from src.face3d.visualize import gen_composed_video
        gen_composed_video(args, device, first_coeff_path, coeff_path, audio_path, os.path.join(save_dir, '3dface.mp4'))
    
    # coeff2video
    data = get_facerender_data(coeff_path, crop_pic_path, first_coeff_path, audio_path, 
                                batch_size, input_yaw_list, input_pitch_list, input_roll_list,
                                expression_scale=args.expression_scale, still_mode=args.still, preprocess=args.preprocess, size=args.size)
    
    result = animate_from_coeff.generate(data, save_dir, pic_path, crop_info, 
                                enhancer=args.enhancer, background_enhancer=args.background_enhancer, preprocess=args.preprocess, img_size=args.size)
    
    video_path = save_dir + '.mp4'
    shutil.move(result, video_path)
    print('The generated video is named:', video_path)

    if not args.verbose:
        shutil.rmtree(save_dir)

    return video_path


def gradio_interface(message, voice, lang, source_image, ref_eyeblink, ref_pose, pose_style, batch_size, size, expression_scale, input_yaw, input_pitch, input_roll, enhancer, background_enhancer, cpu, face3dvis, still, preprocess, verbose, old_version):

    args = Namespace(
        message=message,
        voice=voice,
        lang=lang,
        source_image=source_image,
        ref_eyeblink=ref_eyeblink,
        ref_pose=ref_pose,
        checkpoint_dir='./checkpoints',
        result_dir='./results',
        pose_style=pose_style,
        batch_size=batch_size,
        size=size,
        expression_scale=expression_scale,
        input_yaw=[int(x) for x in input_yaw.split(',')] if input_yaw else None,
        input_pitch=[int(x) for x in input_pitch.split(',')] if input_pitch else None,
        input_roll=[int(x) for x in input_roll.split(',')] if input_roll else None,
        enhancer=enhancer,
        background_enhancer=background_enhancer,
        cpu=cpu,
        face3dvis=face3dvis,
        still=still,
        preprocess=preprocess,
        verbose=verbose,
        old_version=old_version
    )

    if torch.cuda.is_available() and not args.cpu:
        args.device = "cuda"
    else:
        args.device = "cpu"

    return main(args)


iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(placeholder="Enter text to convert to speech", label="Input the text", max_lines=3),
        gr.Radio(label="Language", choices=["en", "fr-fr", "pt-br", "zh-CN", "de", "es", "hi"], value="en"),
        gr.Audio(label="Voice to clone (File)", sources="upload", type="filepath"),
        gr.File(label="Source Image", type="filepath"),
        gr.Number(label="Expression Scale", default=1.0),
        gr.Checkbox(label="Enhancer", placeholder="e.g., gfpgan", optional=True),
        # gr.Checkbox(label="Background Enhancer", placeholder="e.g., realesrgan", optional=True),
        gr.Checkbox(label="Still Mode", default=False),
        gr.Dropdown(label="Preprocess", choices=['crop', 'extcrop', 'resize', 'full', 'extfull'], default='full'),
    ],
    outputs=gr.Video(label="Generated Video"),
    title="Voice Cloning and Animation Tool",
    description="This tool generates a video based on the provided voice, message, and source image."
)

iface.launch()
