import streamlit as st
import requests
from pyngrok import ngrok
import os

# Flask endpoint URL
FLASK_URL = "http://localhost:5000/doyentalker"  # Adjust port if necessary

# Function to run DoyenTalker via Flask API
def run_doyentalker(message, voice, lang, source_image, expression_scale, enhancer, background_enhancer, still, preprocess):
    data = {
        "message": message,
        "voice": voice,
        "lang": lang,
        "source_image": source_image,
        "expression_scale": expression_scale,
        "enhancer": enhancer,
        "background_enhancer": background_enhancer,
        "still": still,
        "preprocess": preprocess,
    }
    response = requests.post(FLASK_URL, json=data)
    return response.json()

# Streamlit UI
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

    # Run button
    if st.button("Run"):
        result = run_doyentalker(message, voice, lang, source_image, expression_scale, enhancer, background_enhancer, still, preprocess)
        st.json(result)  # Display result from Flask API

        # Display the generated video if available
        video_path = result.get('video_path', None)
        if video_path and os.path.exists(video_path):
            st.video(video_path)
        else:
            st.write("No video found.")

if __name__ == "__main__":
    main()
