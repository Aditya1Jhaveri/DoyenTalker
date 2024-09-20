# DoyenTalker

DoyenTalker is a project that uses deep learning techniques to generate personalized avatar videos that speak user-provided text in a specified voice. The system utilizes Coqui TTS for text-to-speech generation, along with
various face rendering and animation techniques to create a video where the given avatar articulates the speech.

## Features

- **Text-to-Speech (TTS)**: Converts a user-provided text message into speech using the Coqui TTS engine.
- **Avatar-based Animation**: Creates a video where a user-selected avatar speaks the generated speech.
- **Customizable Voice**: Users can specify a voice sample to have the avatar speak in that voice.
- **Multilingual Support**: Supports multiple languages for speech synthesis (English, Spanish, French, German, and more).
- **Face Rendering**: Incorporates pose and eye-blink reference videos to enhance facial expression realism.
- **Batch Processing**: Supports the generation of videos in batches, useful for processing long texts by splitting them into smaller chunks.
- **Face Enhancer (Optional)**: Optionally uses face enhancement models such as GFP-GAN or RestoreFormer to improve the quality of the generated avatar’s face.
- **Background Enhancer (Optional)**: Uses Real-ESRGAN to enhance background visuals in the generated video.

## How It Works

- **Input Text** : The user provides a text message that they want the avatar to speak. The text is split into manageable chunks if it exceeds a certain length, ensuring efficient processing.
- **Avatar Image**: An avatar image is selected, which will be used as the visual representation of the character that will speak the text. The system processes this image to prepare it for animation.
- **Voice Sample**: A voice sample is provided by the user. This voice will be used to generate the speech for the text message. The user can choose from a variety of languages and voice options supported by Coqui TTS, such as English, Spanish, French, German, and others.
- **Speech Generation (Coqui TTS)**: Using Coqui TTS, the system generates speech from the input text in the specified voice. The speech is split across multiple audio files if the text has been chunked.
- **Face Rendering and Animation**: The avatar’s face is animated to match the generated speech. The system processes the avatar image using 3DMM (3D Morphable Model) extraction techniques to capture facial expressions. It also integrates reference videos for eye-blinking and head movements to ensure natural-looking animations.
- **Video Generation**: Finally, the audio and animated avatar are combined into a video. The video can be rendered with custom poses, facial expressions, and enhanced visuals using optional face and background enhancement techniques.
- **Output Video**: The result is a video where the avatar accurately speaks the input text in the user-specified voice.

## Installation

This steps need to follow after git clone.

```bash
  pip install uv
```

```bash
  uv venv
  .venv\Scripts\activate
```

```bash
  uv pip install -r requirements.txt
```

```bash
  python main.py  --message_file "/content/drive/MyDrive/voice_cloning_data/test_message.txt" --voice "/content/DoyenTalker/backend/assets/voice/ab_voice.mp3" --lang en --avatar_image "/content/DoyenTalker/backend/assets/avatar/male10.jpeg"
```

## Demo

https://github.com/user-attachments/assets/0f45be53-206f-4b5d-86dd-224ba97d376e

https://github.com/user-attachments/assets/ba2b5743-ad5e-46ca-ac4c-8dad087e7c66





