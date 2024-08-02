from openai import OpenAI
import streamlit as st
import pandas as pd
from audio_recorder_streamlit import audio_recorder

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="KOSODATE AI", page_icon=":material/pets:")
st.title("子育てアドバイスAI")
st.subheader("『子育てで困ったら、これやってみ！』てぃ先生")
voice = "shimmer"

#######################################################
# 音声入力と音声認識（with whisper）
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

# 背景画像の選択とstreamlitによる表示
import base64

def get_image_base64(image_path):
    with open(image_path, 'rb') as img_file:
        b64_string = base64.b64encode(img_file.read()).decode('utf-8')
    return b64_string

background_image = 'data/tsensei_officialweb.png'
base64_image = get_image_base64(background_image)

# カスタムCSSを使って背景画像を設定
page_bg_img = f'''
<style>
.stApp {{
background-image: linear-gradient(rgba(0,0,0,0.2),rgba(0,0,0,0.2)),url("data:image/png;base64,{base64_image}") ;
background-size: cover;
background-repeat: no-repeat;
background-attachment: fixed;
}}
</style>
'''
#background-image: url("data:image/png;base64,{base64_image}");
st.markdown(page_bg_img, unsafe_allow_html=True)
############################################################################

# data
df = pd.read_csv('data/kosodate.csv')
df = df.drop("ID", axis=1)
data2 = df.to_string()

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
"""__MSG__"""
'''
#特に、__MSG2__になりきってください。
template = template.replace('__MSG__', data2.replace('"', ''))
#template = template.replace('__MSG2__', character.replace('"', ''))

# OpenAIのモデルを指定
if "openai_model" not in st.session_state:
    #st.session_state["openai_model"] = "gpt-3.5-turbo"
    st.session_state["openai_model"] = "gpt-4o-mini"

# チャットの履歴 messages を初期化（一つ一つの messages は {role, content} の形式）
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages = [{'role': 'system', 'content': template}]

# それまでのメッセージを全て表示したままにする（このloopがないと、同じ場所を更新しながら会話が続く）
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
    prompt = st.chat_input("しつもんは？")

# 音声入力がある場合、テキストに変換
if audio_bytes:
    audio_transcript = audio_to_text(audio_bytes)
    if audio_transcript:
        st.session_state.audio_transcript = audio_transcript

# テキスト入力がある場合、音声入力をリセット
if prompt and 'audio_transcript' in st.session_state:
    del st.session_state.audio_transcript

input_text = st.session_state.audio_transcript if 'audio_transcript' in st.session_state else prompt

# old codes
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
