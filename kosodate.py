import pandas as pd
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="KOSODATE AI", page_icon=":material/pets:")
st.title("子育てアドバイスAI")
st.subheader("『子育てで困ったら、これやってみ！』てぃ先生")
voice = "shimmer"

def write_audio_file(file_path, audio_bytes):
    with open(file_path, "wb") as audio_file:
        audio_file.write(audio_bytes)

def audio_to_text(audio_bytes):
    write_audio_file("recorded_audio.wav", audio_bytes)
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=open("recorded_audio.wav", "rb"),
    )
    return transcript.text

# data
df = pd.read_csv('data/kosodate.csv')
df = df.drop("ID", axis=1)
data = df.to_string()

# template
template = '''
あなたは熟練した日本人男性の保育士「てぃ先生」です。
子育てに奮闘するママ・パパがその悩みや言い換えるべき声掛けを質問するので、それに回答してください。

### 条件
- 全ての質問に対して、返答内容に関する以下の「資料」を参照した上で答えてください。
- 質問者は子育て中で、言うことを聞かない未熟な幼児に対する悩みを入力します。
- あるいは、つい望ましくない声掛けをしようとしており、その文章が入力されます。
- 入力に対して、あなたは適切なアドバイスをするか、声掛けを望ましいものに言い換えた「言い換え」を教えてください。
- 質問者は子育てに疲れていたり、動転した状況ですので、質問者を安心させるように答えてください。
- 極めて短い文章で答えて。どうしてその回答になったのかの「理由」を質問されたら、続けて答えてください。

### 資料
"""__CSV__"""
'''

template = template.replace('__CSV__', data.replace('"', ''))

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages = [{'role': 'system', 'content': template}]

col1, col2 = st.columns(2)
with col1:
    audio_bytes = audio_recorder(
    text="", recording_color="#f21835", neutral_color="#2EF218", icon_name="microphone", icon_size="2x",
    pause_threshold=5.0, sample_rate=41_000
)
with col2:
    prompt = st.chat_input("悩み・言い換え？")

if audio_bytes:
    audio_transcript = audio_to_text(audio_bytes)
    if audio_transcript:
        st.session_state.audio_transcript = audio_transcript

if prompt and 'audio_transcript' in st.session_state:
    del st.session_state.audio_transcript

input_text = st.session_state.audio_transcript if 'audio_transcript' in st.session_state else prompt

if input_text:
    st.session_state.messages.append({"role": "user", "content": input_text})
    with st.chat_message("user"):
        st.markdown(input_text)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model = st.session_state["openai_model"],
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream = True,
            temperature = 0.5,
        )
        response = st.write_stream(stream)
        
        user_input = response
        if user_input:
            try:
                response_audio = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=user_input,
                )
                output_file = "output.mp3"
                response_audio.stream_to_file(output_file)
                st.audio(output_file, autoplay = True)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
        else:
            st.warning("テキストを入力してください。")
    st.session_state.messages.append({"role": "assistant", "content": response})
