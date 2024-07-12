import streamlit as st
import subprocess
import time 
import os
import tempfile

def main():
    st.title("DoyenTalker")
    
    # Input fields
    message = st.text_area("Enter the message text")
    voice = st.file_uploader("Upload Voice File", type=["wav", "mp3"])
    lang = st.selectbox("Select Language", ["en", "es", "de", "fr"])  # Add more languages as needed
    source_image = st.file_uploader("Upload Source Image", type=["png", "jpg", "jpeg"])
    expression_scale = st.number_input("Expression Scale", min_value=0.1, max_value=2.0, value=1.0)
    enhancer = st.checkbox("Face Enhancer")
    background_enhancer = st.checkbox("Background Enhancer")
    still = st.checkbox("Crop Back to Original Videos for Full Body Animation")
    preprocess = st.selectbox("Preprocess", ['crop', 'extcrop', 'resize', 'full', 'extfull'])

    if st.button("Run"):
        with tempfile.TemporaryDirectory() as tempdir:
            # Save the text message to a temporary file
            message_file_path = os.path.join(tempdir, "message.txt")
            with open(message_file_path, "w") as f:
                f.write(message)

            # Save the voice file to a temporary directory
            if voice:
                voice_file_path = os.path.join(tempdir, voice.name)
                with open(voice_file_path, "wb") as f:
                    f.write(voice.read())
            else:
                st.error("Please upload a voice file")
                return

            # Save the source image to a temporary directory
            if source_image:
                source_image_path = os.path.join(tempdir, source_image.name)
                with open(source_image_path, "wb") as f:
                    f.write(source_image.read())
            else:
                st.error("Please upload a source image")
                return
            
            # Define the result directory
            result_dir = "./results"
            path = os.path.join(result_dir, str(int(time.time())))
            os.makedirs(path, exist_ok=True)

            # Prepare command
            command = [
                "python", "main.py",
                "--message_file", message_file_path,
                "--voice", voice_file_path,
                "--lang", lang,
                "--source_image", source_image_path,
                "--expression_scale", str(expression_scale),
                "--preprocess", preprocess,
                "--result_dir", path
            ]

            if enhancer:
                command.extend(["--enhancer", "gfpgan"])  # Replace with actual enhancer if needed

            if background_enhancer:
                command.extend(["--background_enhancer", "realesrgan"])  # Replace with actual background enhancer if needed

            if still:
                command.append("--still")

            # Run command
            st.write("Running command:", " ".join(command))
            result = subprocess.run(command, capture_output=True, text=True)
            st.text(result.stdout)
            st.text(result.stderr)
            
            # Display the generated video
            video_path = os.path.join(path, 'result.mp4')  # Adjust the path based on your output
            if os.path.exists(video_path):
                st.video(video_path)
            else:
                st.write("No video found at", video_path)

if __name__ == "__main__":
    main()
