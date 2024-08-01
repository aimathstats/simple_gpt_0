from openai import OpenAI
import streamlit as st
import pandas as pd
from audio_recorder_streamlit import audio_recorder

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="honyaku konnyaku", page_icon=":material/pets:")
st.title("ほんやくコンニャク")
lang = st.radio("何語に翻訳？", ["英語", "フランス語", "中国語"], horizontal = True)
voice = "alloy"

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

template = '''
あなたは翻訳をするアシスタントです。
私は主に日本語を入力するので、それを__MSG__に翻訳して、文章を出力してください。
出力するのは__MSG__だけにして、余計なことは付け加えないでください。
'''
template = template.replace('__MSG__', lang.replace('"', ''))

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages = [{'role': 'system', 'content': template}]

#for message in st.session_state.messages[1:]:
#    with st.chat_message(message["role"]):
#        st.markdown(message["content"]) # 表示する（一瞬ですべて書き下す）

# 入力（音声/テキスト）
col1, col2 = st.columns(2)
with col1:
    audio_bytes = audio_recorder(
    text="", recording_color="#f21835", #recording_color="#e8b62c",
    neutral_color="#2EF218", icon_name="microphone", icon_size="2x",
    pause_threshold=5.0, sample_rate=41_000
)
with col2:
    prompt = st.chat_input("日本語を話して")

# 音声入力がある場合、テキストに変換
if audio_bytes:
    audio_transcript = audio_to_text(audio_bytes)
    if audio_transcript:
        st.session_state.audio_transcript = audio_transcript

# テキスト入力がある場合、音声入力をリセット
if prompt and 'audio_transcript' in st.session_state:
    del st.session_state.audio_transcript

input_text = st.session_state.audio_transcript if 'audio_transcript' in st.session_state else prompt

if input_text:
    # messagesにユーザーのプロンプトを追加
    st.session_state.messages.append({"role": "user", "content": input_text})

    # ユーザーのアイコンで、promptをそのまま表示
    with st.chat_message("user"):
        st.markdown(input_text)

    # AIのアイコンで
    with st.chat_message("assistant"):
        # ChatGPTの返答をstreamに格納
        stream = client.chat.completions.create(
            model = st.session_state["openai_model"],
            # 会話履歴をすべて参照して渡す
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream = True,
            temperature = 0.5,
        )
        # AIの返答を流れるように出力
        response = st.write_stream(stream)
        
        # 音声合成（with tts-1）
        user_input = response
        if user_input:
            try:
                # 音声合成リクエストの送信
                response_audio = client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=user_input,
                )
                # 結果をファイルに保存
                output_file = "output.mp3"
                response_audio.stream_to_file(output_file)
                # ユーザに音声ファイルをダウンロードするオプションを提供
                st.audio(output_file, autoplay = True)
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
        else:
            st.warning("テキストを入力してください。")
    
    # messagesにAIの返答を格納
    st.session_state.messages.append({"role": "assistant", "content": response})
    #　ここで一旦終わり、入力待機となる
