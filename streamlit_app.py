import streamlit as st
import requests
import os
import tempfile


# Flask endpoint URL
FLASK_URL = "http://localhost:5000/doyentalker"  # Adjust port if necessary

# Function to run DoyenTalker via Flask API
def run_doyentalker(message, voice, lang, source_image, expression_scale, enhancer, background_enhancer, still, preprocess):
    # Prepare data to send to Flask API
    data = {
        "message": message,
        "lang": lang,
        "expression_scale": expression_scale,
        "enhancer": enhancer,
        "background_enhancer": background_enhancer,
        "still": still,
        "preprocess": preprocess,
    }

    # Handle voice file
    if voice:
        voice_filename = save_uploaded_file(voice, "voice")
        data["voice"] = voice_filename
        
        print("Voice_file: ",voice)
        
        print("voice_file name:", voice_filename)

    # Handle source image file
    if source_image:
        image_filename = save_uploaded_file(source_image, "image")
        data["source_image"] = image_filename
        
        print("image: ", source_image)
        print("image_name: ",image_filename )

    # Send POST request to Flask API
    response = requests.post(FLASK_URL, json=data)
    print("Data: ", data)
    # Check if the request was successful
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to get response from server"}

# Function to save uploaded file and return the file path
def save_uploaded_file(uploaded_file, file_type):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file.close()
        return temp_file.name

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
        print("Result: ", result)
        st.json(result)  # Display result from Flask API

        # Display the generated video if available
        video_path = result.get('video_path', None)
        if video_path and os.path.exists(video_path):
            st.video(video_path)
        else:
            st.write("No video found.")

if __name__ == "__main__":
    main()
