import React, { useState } from "react";
import axios from "axios";
import { ReactMic } from "react-mic";
import { useFormik } from "formik";
import * as Yup from "yup";
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

import video from "./results/AB_social_media.mp4";

function App() {
  const [audioBlob, setAudioBlob] = useState(null);
  const [audioURL, setAudioURL] = useState("");
  const [videoURL, setVideoURL] = useState("");

  const handleStartRecording = () => formik.setFieldValue("recording", true);
  const handleStopRecording = () => formik.setFieldValue("recording", false);

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

  const handleData = (recordedBlob) => {
    setAudioBlob(recordedBlob.blob);
    setAudioURL(URL.createObjectURL(recordedBlob.blob));
    formik.setFieldValue(
      "audioFile",
      new File([audioBlob], "recorded_audio.wav", { type: "audio/wav" })
    );
  };

  const formik = useFormik({
    initialValues: {
      avatarChoice: "predefined_avatar",
      voiceChoice: "predefined_voice",
      inputText: "",
      languageAccent: "en",
      selectedVoice: "trump_voice",
      selectedAvatar: "male1",
      customAvatar: null,
      customAvatarName: "",
      voiceFile: null,
      voiceName: "",
      recording: false,
      audioFile: null,
    },
    validationSchema: Yup.object({
      avatarChoice: Yup.string().required("Avatar choice is required"),
      voiceChoice: Yup.string().required("Voice choice is required"),
      inputText: Yup.string().required("Input text is required"),
      languageAccent: Yup.string().required("Language accent is required"),
      selectedVoice: Yup.string().required("Voice selection is required"),
      selectedAvatar: Yup.string().required("Avatar selection is required"),
    }),
    onSubmit: (values) => {
      console.log("Form data:", values);

      let avatar_selected =
        values.avatarChoice === "predefined_avatar"
          ? values.selectedAvatar
          : values.customAvatar;

      let voice_selected =
        values.voiceChoice === "voice_file"
          ? values.voiceFile
          : values.voiceChoice === "mic"
          ? values.audioFile
          : values.selectedVoice;

      axios
        .post(
          "http://127.0.0.1:5000/doyentalker",
          {
            message: values.inputText,
            lang: values.languageAccent,
            voice_name: voice_selected,
            avatar_name: avatar_selected,
          },
          {
            headers: { "Content-Type": "multipart/form-data" },
          }
        )
        .then((response) => {
          console.log("API response:", response);
          setVideoURL(response.data.video_url);
        })
        .catch((error) => {
          console.error("API error:", error);
        });
    },
  });

  const handleSetTestVideo = () => {
    const testVideoURL = video;
    setVideoURL(testVideoURL);
  };

  const handleClear = () => {
    formik.resetForm();
    setAudioBlob(null);
    setAudioURL("");
    setVideoURL("");
  };

  return (
    <Container maxWidth="md">
      <Box
        sx={{
          bgcolor: "#F5F5E1",
          color: "black",
          p: 3,
          borderRadius: 2,
          margin: 5,
        }}
      >
        <h2>DoyenTalker</h2>
        <form onSubmit={formik.handleSubmit}>
          <FormControl component="fieldset" fullWidth>
            <FormLabel component="legend">
              How would you like to choose the Avatar?
            </FormLabel>
            <RadioGroup
              row
              aria-label="avatar"
              name="avatarChoice"
              value={formik.values.avatarChoice}
              onChange={formik.handleChange}
            >
              <FormControlLabel
                value="predefined_avatar"
                control={<Radio />}
                label="Pre-defined Avatar"
              />
              <FormControlLabel
                value="custom_avatar"
                control={<Radio />}
                label="Custom Avatar"
              />
            </RadioGroup>
          </FormControl>

          {formik.values.avatarChoice === "predefined_avatar" ? (
            <FormControl variant="filled" fullWidth sx={{ mt: 2 }}>
              <InputLabel>Select Avatar</InputLabel>
              <Select
                name="selectedAvatar"
                value={formik.values.selectedAvatar}
                onChange={formik.handleChange}
                error={
                  formik.touched.selectedAvatar &&
                  Boolean(formik.errors.selectedAvatar)
                }
                helperText={
                  formik.touched.selectedAvatar && formik.errors.selectedAvatar
                }
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
                <MenuItem value="male10">Male 10</MenuItem>
                <MenuItem value="female1">Female 1</MenuItem>
                <MenuItem value="female2">Female 2</MenuItem>
                <MenuItem value="female3">Female 3</MenuItem>
                <MenuItem value="female4">Female 4</MenuItem>
                <MenuItem value="female5">Female 5</MenuItem>
                <MenuItem value="female6">Female 6</MenuItem>
              </Select>
            </FormControl>
          ) : (
            <>
              <p style={{ color: "#6E6868" }}>
                Upload the avatar image according to your choice
              </p>
              <Box sx={{ mt: 2, display: "flex", alignItems: "center" }}>
                <Button
                  variant="contained"
                  component="label"
                  sx={{ bgcolor: "blue" }}
                >
                  Upload Avatar
                  <input
                    accept="image/*"
                    type="file"
                    hidden
                    onChange={(event) => {
                      const file = event.target.files[0];
                      formik.setFieldValue("customAvatar", file);
                      formik.setFieldValue("customAvatarName", file.name);
                    }}
                  />
                </Button>
                {formik.values.customAvatarName && (
                  <Typography variant="body1" sx={{ ml: 2 }}>
                    {formik.values.customAvatarName}
                  </Typography>
                )}
              </Box>
            </>
          )}

          <hr style={{ marginTop: 20 }} />

          <FormControl component="fieldset" fullWidth sx={{ mt: 2 }}>
            <FormLabel component="legend">
              How would you like to choose the voice?
            </FormLabel>
            <RadioGroup
              row
              aria-label="voice"
              name="voiceChoice"
              value={formik.values.voiceChoice}
              onChange={formik.handleChange}
            >
              <FormControlLabel
                value="predefined_voice"
                control={<Radio />}
                label="Pre-defined Voice"
              />
              <FormControlLabel value="mic" control={<Radio />} label="Mic" />
              <FormControlLabel
                value="voice_file"
                control={<Radio />}
                label="Voice File"
              />
            </RadioGroup>
          </FormControl>

          {formik.values.voiceChoice === "predefined_voice" && (
            <FormControl variant="filled" fullWidth sx={{ mt: 2 }}>
              <InputLabel>Select Voice</InputLabel>
              <Select
                name="selectedVoice"
                value={formik.values.selectedVoice}
                onChange={formik.handleChange}
                error={
                  formik.touched.selectedVoice &&
                  Boolean(formik.errors.selectedVoice)
                }
                helperText={
                  formik.touched.selectedVoice && formik.errors.selectedVoice
                }
              >
                <MenuItem value="trump_voice">Trump Voice</MenuItem>
                <MenuItem value="PC_voice">Michelle Obama Voice</MenuItem>
                <MenuItem value="beyonce_voice">Beyonce Voice</MenuItem>
                <MenuItem value="emma_waston_voice">Emma Watson Voice</MenuItem>
                <MenuItem value="ab_voice">Amitabh Bachchan Voice</MenuItem>
                <MenuItem value="modi_voice">Modi Voice</MenuItem>
                <MenuItem value="srk_voice">SRK Voice</MenuItem>
                <MenuItem value="PC_voice">Priyanka Chopra Voice</MenuItem>
              </Select>
            </FormControl>
          )}

          {formik.values.voiceChoice === "mic" && (
            <Box sx={{ mt: 2 }}>
              <p style={{ color: "#6E6868" }}>
                Read the text below to clone your voice
              </p>
              <Typography variant="body1" sx={{ mb: 2 }} align="justify">
                {speech}
              </Typography>
              <div style={{ display: "flex", flexDirection: "column" }}>
                <ReactMic
                  record={formik.values.recording}
                  onStop={handleData}
                />
              </div>

              <Box
                sx={{
                  mt: 2,
                  display: "flex",
                  justifyContent: "space-between",
                }}
              >
                <Button
                  onClick={handleStartRecording}
                  variant="contained"
                  color="primary"
                  className=""
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

          {formik.values.voiceChoice === "voice_file" && (
            <>
              <p style={{ color: "#6E6868" }}>
                Upload the voice file according to your choice
              </p>

              <Box sx={{ mt: 2, display: "flex", alignItems: "center" }}>
                <Button
                  variant="contained"
                  component="label"
                  sx={{ bgcolor: "blue" }}
                >
                  Upload Voice
                  <input
                    accept="audio/*"
                    type="file"
                    hidden
                    onChange={(event) => {
                      const file = event.target.files[0];
                      formik.setFieldValue("voiceFile", file);
                      formik.setFieldValue("voiceName", file.name);
                    }}
                  />
                </Button>
                {formik.values.voiceName && (
                  <Typography variant="body1" sx={{ ml: 2 }}>
                    {formik.values.voiceName}
                  </Typography>
                )}
              </Box>
            </>
          )}
          <hr style={{ marginTop: 20 }} />

          <Box sx={{ mt: 3 }}>
            <TextField
              label="Input Text"
              name="inputText"
              variant="filled"
              placeholder="Enter the text you want to generate for speech"
              multiline
              rows={4}
              fullWidth
              value={formik.values.inputText}
              onChange={formik.handleChange}
              error={
                formik.touched.inputText && Boolean(formik.errors.inputText)
              }
              helperText={formik.touched.inputText && formik.errors.inputText}
            />
          </Box>

          <hr style={{ marginTop: 20 }} />

          <FormControl variant="filled" fullWidth sx={{ mt: 2 }}>
            <InputLabel>Select the language accent of speaker</InputLabel>
            <Select
              name="languageAccent"
              value={formik.values.languageAccent}
              onChange={formik.handleChange}
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

          <Box sx={{ mt: 2, display: "flex", justifyContent: "space-between" }}>
            <Button
              type="button"
              color="error"
              variant="contained"
              onClick={handleClear}
            >
              Clear
            </Button>
            <Button type="submit" color="success" variant="contained">
              Submit
            </Button>
            <Button
              type="button"
              color="primary"
              variant="contained"
              onClick={handleSetTestVideo}
            >
              test
            </Button>
          </Box>
          {videoURL && (
            <Box
              sx={{
                mt: 3,
                border: "1px solid #ccc",
                borderRadius: 1,
                p: 2,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                bgcolor: "#e0e0e0",
              }}
            >
              <Typography variant="h6">Generated Video:</Typography>
              <video src={videoURL} controls width="100%" />
            </Box>
          )}
        </form>
      </Box>
    </Container>
  );
}

export default App;
