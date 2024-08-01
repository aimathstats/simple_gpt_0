import streamlit as st
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
import os
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

###########################################
# 画像生成（DALL-E-3）
#st.title("画像生成AI")
#prompt = st.text_input("作りたい画像の説明をかいて")

#if st.button("生成"):
#    if prompt:
#        response = client.images.generate(
#            model="dall-e-3",
#            prompt=prompt,
#            size="1024x1024",
#            quality="standard",
#            n=1
#        )
#
#        # 生成された画像のURLを取得して表示
#        image_url = response.data[0].url
#        st.image(image_url)
#    else:
#        st.warning("画像の説明を入力して")

#########################################
picture = st.camera_input("Take a picture")

if picture:
    st.image(picture)

#########################################
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
