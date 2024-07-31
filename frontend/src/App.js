import React, { useState } from "react";
import axios from "axios";
import { ReactMic } from "react-mic";
import {
  Container,
  Box,
  TextField,
  Button,
  Radio,
  RadioGroup,
  FormControlLabel,
  FormControl,
  FormLabel,
  Select,
  MenuItem,
  InputLabel,
  Typography,
} from "@mui/material";

function App() {
  const [avatarChoice, setAvatarChoice] = useState("predefined_avatar");
  const [voiceChoice, setVoiceChoice] = useState("predefined_voice");
  const [customAvatar, setCustomAvatar] = useState(null);
  const [customAvatarName, setCustomAvatarName] = useState("");
  const [voiceFile, setVoicefile] = useState(null);
  const [voiceName, setVoicename] = useState("");
  const [inputText, setInputText] = useState("");
  const [languageAccent, setLanguageAccent] = useState("en");
  const [selectedVoice, setSelectedVoice] = useState("trump_voice");
  const [selectedAvatar, setSelectedAvatar] = useState("male1");

  // States for ReactMic
  const [record, setRecord] = useState(false);
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioURL, setAudioURL] = useState("");

  const handleStartRecording = () => setRecord(true);
  const handleStopRecording = () => setRecord(false);

  const handleData = (recordedBlob) => {
    setAudioBlob(recordedBlob.blob);
    setAudioURL(URL.createObjectURL(recordedBlob.blob));
  };

  // Convert audioBlob to a file
  let audioFile = null;
  if (audioBlob) {
    audioFile = new File([audioBlob], "recorded_audio.wav", {
      type: "audio/wav",
    });
  }

  let avatar_name = "";

  if (avatarChoice === "predefined_avatar") {
    avatar_name = selectedAvatar;
  } else {
    avatar_name = customAvatar;
  }

  let voice_name = "";

  if (voiceChoice === "voice_file") {
    voice_name = voiceFile;
  } else if (voiceChoice === "mic") {
    voice_name = audioFile;
  } else {
    voice_name = selectedVoice;
  }

  let speech =
    "Ladies and gentlemen,\n\n" +
    "Education is the cornerstone of our society, shaping the minds and futures of our youth. It is not merely about acquiring knowledge from textbooks, " +
    "but also about developing critical thinking, creativity, and the ability to adapt to an ever-changing world. Every child deserves access to quality education, " +
    "as it lays the foundation for personal growth, career success, and civic responsibility.\n\n" +
    "Investing in education means investing in the future. It empowers individuals to break the cycle of poverty, fosters innovation, and drives economic development. " +
    "In today's digital age, it is crucial to integrate technology into the learning process, making education more accessible and engaging for all.\n\n" +
    "Teachers play a pivotal role in this journey. Their dedication and passion inspire students to reach their full potential. Therefore, we must support and value our educators, " +
    "providing them with the resources and training they need to thrive.\n\n" +
    "Let us work together to create an inclusive and equitable education system that nurtures the talents of every student, ensuring a brighter, more prosperous future for all.\n\n" +
    "Thank you.";

  const handleSubmit = (event) => {
    event.preventDefault();
    const formData = {
      avatarChoice,
      voiceChoice,
      inputText,
      languageAccent,
      avatar_name,
      voice_name,
    };
    console.log("Form data:", formData);
    axios
      .post(
        "http://127.0.0.1:5000/doyentalker",
        {
          message: inputText,
          lang: languageAccent,
          voice_name: voice_name,
          avatar_name: avatar_name,
        },
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      )
      .then((response) => {
        console.log("API response:", response);
      })
      .catch((error) => {
        console.error("API error:", error);
      });
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ bgcolor: "#f5f5f5", color: "black", p: 3, borderRadius: 2 }}>
        <h2>DoyenTalker</h2>
        <form onSubmit={handleSubmit}>
          <FormControl component="fieldset" fullWidth>
            <FormLabel component="legend">
              How would you like to choose the Avatar?
            </FormLabel>
            <RadioGroup
              row
              aria-label="avatar"
              name="avatarChoice"
              value={avatarChoice}
              onChange={(e) => setAvatarChoice(e.target.value)}
            >
              <FormControlLabel
                value="predefined_avatar"
                control={<Radio />}
                label="Predefined Avatar"
              />
              <FormControlLabel
                value="custom_avatar"
                control={<Radio />}
                label="Custom Avatar"
              />
            </RadioGroup>
          </FormControl>

          {avatarChoice === "predefined_avatar" ? (
            <FormControl variant="filled" fullWidth sx={{ mt: 2 }}>
              <InputLabel>Select the Avatar</InputLabel>
              <Select
                name="selectedAvatar"
                value={selectedAvatar}
                onChange={(e) => setSelectedAvatar(e.target.value)}
              >
                <MenuItem value="male1">Male 1</MenuItem>
                <MenuItem value="male2">Male 2</MenuItem>
                <MenuItem value="male3">Male 3</MenuItem>
                <MenuItem value="male4">Male 4</MenuItem>
                <MenuItem value="male5">Male 5</MenuItem>
                <MenuItem value="male6">Male 6</MenuItem>
                <MenuItem value="male7">Male 7</MenuItem>
                <MenuItem value="male8">Male 8</MenuItem>
                <MenuItem value="male9">Male 9</MenuItem>
                <MenuItem value="female1">Female 1</MenuItem>
                <MenuItem value="female2">Female 2</MenuItem>
                <MenuItem value="female3">Female 3</MenuItem>
                <MenuItem value="female4">Female 4</MenuItem>
                <MenuItem value="female5">Female 5</MenuItem>
                <MenuItem value="female6">Female 6</MenuItem>
              </Select>
            </FormControl>
          ) : (
            <Box sx={{ mt: 2, display: "flex", alignItems: "center" }}>
              <Button
                variant="contained"
                component="label"
                sx={{ bgcolor: "blue" }}
              >
                Upload Image
                <input
                  accept="image/*"
                  type="file"
                  hidden
                  onChange={(event) => {
                    const file = event.target.files[0];
                    setCustomAvatar(file);
                    setCustomAvatarName(file.name);
                  }}
                />
              </Button>
              {customAvatarName && (
                <Typography variant="body1" sx={{ ml: 2 }}>
                  {customAvatarName}
                </Typography>
              )}
            </Box>
          )}

          <FormControl component="fieldset" fullWidth sx={{ mt: 2 }}>
            <FormLabel component="legend">
              How would you like to choose the voice?
            </FormLabel>
            <RadioGroup
              row
              aria-label="voice"
              name="voiceChoice"
              value={voiceChoice}
              onChange={(e) => setVoiceChoice(e.target.value)}
            >
              <FormControlLabel
                value="predefined_voice"
                control={<Radio />}
                label="Predefined Voice"
              />
              <FormControlLabel value="mic" control={<Radio />} label="Mic" />
              <FormControlLabel
                value="voice_file"
                control={<Radio />}
                label="Voice File"
              />
            </RadioGroup>
          </FormControl>

          {voiceChoice === "predefined_voice" && (
            <FormControl variant="filled" fullWidth sx={{ mt: 2 }}>
              <InputLabel>Select Voice</InputLabel>
              <Select
                name="selectedVoice"
                value={selectedVoice}
                onChange={(e) => setSelectedVoice(e.target.value)}
              >
                <MenuItem value="trump_voice">Trump Voice</MenuItem>
                <MenuItem value="ab_voice">Amitabh Bachchan Voice</MenuItem>
                <MenuItem value="beyonce_voice">Beyonce Voice</MenuItem>
                <MenuItem value="emma_waston_voice">Emma Waston Voice</MenuItem>
                <MenuItem value="modi_voice">Modi Voice</MenuItem>
                <MenuItem value="srk_voice">SRK Voice</MenuItem>
                <MenuItem value="PC_voice">Priyanka Chopra Voice</MenuItem>
              </Select>
            </FormControl>
          )}

          {voiceChoice === "mic" && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="body1" sx={{ ml: 2 }}>
                {speech}
              </Typography>
              <ReactMic record={record} onStop={handleData} />
              <Box
                sx={{ mt: 2, display: "flex", justifyContent: "space-between" }}
              >
                <Button
                  onClick={handleStartRecording}
                  variant="contained"
                  color="primary"
                >
                  Start Recording
                </Button>
                <Button
                  onClick={handleStopRecording}
                  variant="contained"
                  color="secondary"
                >
                  Stop Recording
                </Button>
              </Box>
              {audioURL && (
                <audio controls src={audioURL} style={{ marginTop: "10px" }} />
              )}
            </Box>
          )}

          {voiceChoice === "voice_file" && (
            <Box sx={{ mt: 2, display: "flex", alignItems: "center" }}>
              <Button
                variant="contained"
                component="label"
                sx={{ bgcolor: "blue" }}
              >
                Upload Voice File
                <input
                  accept=".mp3, .wav"
                  type="file"
                  hidden
                  onChange={(event) => {
                    const file = event.target.files[0];
                    setVoicefile(file);
                    setVoicename(file.name);
                  }}
                />
              </Button>
              {voiceName && (
                <Typography variant="body1" sx={{ ml: 2 }}>
                  {voiceName}
                </Typography>
              )}
            </Box>
          )}

          <Box sx={{ mt: 3 }}>
            <TextField
              label="Input Text"
              variant="outlined"
              placeholder="Enter the text you want to generate for speech"
              multiline
              rows={4}
              fullWidth
              sx={{ bgcolor: "white", borderRadius: 1 }}
              name="inputText"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
            />
          </Box>

          <FormControl variant="filled" fullWidth sx={{ mt: 2 }}>
            <InputLabel>Select the language accent of speaker</InputLabel>
            <Select
              name="languageAccent"
              value={languageAccent}
              onChange={(e) => setLanguageAccent(e.target.value)}
            >
              <MenuItem value="en">English</MenuItem>
              <MenuItem value="es">Spanish</MenuItem>
              <MenuItem value="fr">French</MenuItem>
              <MenuItem value="de">German</MenuItem>
              <MenuItem value="it">Italian</MenuItem>
              <MenuItem value="pt">Portuguese</MenuItem>
              <MenuItem value="pl">Polish</MenuItem>
              <MenuItem value="tr">Turkish</MenuItem>
              <MenuItem value="ru">Russian</MenuItem>
              <MenuItem value="nl">Dutch</MenuItem>
              <MenuItem value="cs">Czech</MenuItem>
              <MenuItem value="ar">Arabic</MenuItem>
              <MenuItem value="zh-cn">Chinese (Simplified)</MenuItem>
              <MenuItem value="hu">Hungarian</MenuItem>
              <MenuItem value="ko">Korean</MenuItem>
              <MenuItem value="ja">Japanese</MenuItem>
              <MenuItem value="hi">Hindi</MenuItem>
            </Select>
          </FormControl>

          <Box sx={{ mt: 3, display: "flex", justifyContent: "space-between" }}>
            <Button type="submit" variant="contained" color="primary">
              Submit
            </Button>
          </Box>

          <Box
            sx={{
              mt: 3,
              border: "1px solid #ccc",
              borderRadius: 1,
              p: 2,
              height: "150px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              bgcolor: "#e0e0e0",
            }}
          >
            <p>Output</p>
          </Box>
        </form>
      </Box>
    </Container>
  );
}

export default App;
