import streamlit as st
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
import os
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def write_audio_file(file_path, audio_bytes):
    with open(file_path, "wb") as audio_file:
        audio_file.write(audio_bytes)

audio_bytes = audio_recorder(
    text="click and speak>>>",
    recording_color="#e8b62c",
    neutral_color="#6aa36f",
    icon_name="microphone-lines",
    icon_size="3x",
    pause_threshold=2.0,
    sample_rate=41_000
)  

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    write_audio_file("recorded_audio.wav", audio_bytes)

    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=open("recorded_audio.wav", "rb"),
    )
    st.text(transcript.text)
