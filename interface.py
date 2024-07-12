import gradio as gr
from main import main

def interface(message, voice, lang, source_image, expression_scale, enhancer, still, preprocess):

    args = {
        "--message_file": message,
        "--voice": voice,
        "--lang": lang,
        "--source_image": source_image,
        "--expression_scale": expression_scale,
        "--enhancer": enhancer,
        "--still": still,
        "--preprocess": preprocess,
    }
    
    main(args)

iface = gr.Interface(
    fn=interface,
    inputs=[
        gr.Textbox(placeholder="Enter text to convert to speech", label="Input the text", max_lines=3),
        gr.Radio(label="Language", choices=["en", "fr-fr", "pt-br", "zh-CN", "de", "es", "hi"], value="en"),
        gr.Audio(label="Voice to clone (File)",sources="upload", type="filepath"),
        gr.File(label="Source Image", type="filepath"),
        gr.Number(label="Expression Scale", value=1.0),
        gr.Checkbox(label="Enhancer"),
        gr.Checkbox(label="Still Mode", value=False),
        gr.Dropdown(label="Preprocess", choices=['crop', 'extcrop', 'resize', 'full', 'extfull'], value='full'),
    ],
    outputs=gr.Video(label="Generated Video"),
    title="DoyenTalker",
    description="This tool generates a video based on the provided voice, message, and source image."
)

iface.launch(debug=True)
