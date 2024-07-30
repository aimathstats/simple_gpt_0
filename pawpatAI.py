from openai import OpenAI
import streamlit as st
import pandas as pd

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="Paw patrol AI", page_icon=":material/pets:")
st.title("パウパトAI")
st.subheader("パウパトについて何でも聞いてみよう！")
#character = st.radio("", ["みんな","ケント", "チェイス"], horizontal = True)
character = "ケント"
voice = "alloy"

#########################################
#user_input = st.text_area("テキストを入力してください", "Hello, Paw patrol!", height=200)
#voice = st.radio("voice", ["alloy", "echo", "fable", "onyx", "nova", "shimmer"], horizontal = True)
#if st.button('音声合成'):
#    if user_input:
#        try:
#            response = client.audio.speech.create(
#                model="tts-1",
#                voice=voice,
#                input=user_input,
#            )
#            output_file = "output.mp3"
#            response.stream_to_file(output_file)
#            st.audio(output_file)
#        except Exception as e:
#            st.error(f"エラーが発生しました: {e}")
#    else:
#        st.warning("テキストを入力してください。")
############################################################################

# 背景画像の選択とstreamlitによる表示
import base64

# 画像のパス
background_image = 'data/paw_figure1.png'

# 画像をBase64エンコードする関数
def get_image_base64(image_path):
    with open(image_path, 'rb') as img_file:
        b64_string = base64.b64encode(img_file.read()).decode('utf-8')
    return b64_string

# 画像をBase64エンコード
base64_image = get_image_base64(background_image)

# カスタムCSSを使って背景画像を設定
page_bg_img = f'''
<style>
.stApp {{
background-image: url("data:image/png;base64,{base64_image}");
background-size: cover;
background-repeat: no-repeat;
background-attachment: fixed;
}}
</style>
'''

# カスタムCSSを挿入
st.markdown(page_bg_img, unsafe_allow_html=True)
############################################################################

# data
df = pd.read_csv('data/paw_data.csv')
data2 = df.to_string()

# template
template = '''
あなたはカナダ製の子供用アニメ「パウパトロール」について何でも応答するAIです。
指定された役割があれば、キャラクターのセリフに応じて答えてあげてください。
質問者は基本的に未就学の子供なので、簡単で分かりやすい日本語で答えてください。

### 条件
- 全ての質問に対して、返答内容に関する以下の「資料」を参照した上で、役割になりきって答えてください。
- キャラクターの名前を呼ばれたら、そのキャラクターのセリフを忠実に再現して下さい。そのキャラクターが言いそうなことを言ってください。
- ライダーは別名ケントであることに注意してください。

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
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"]) # 表示する（一瞬ですべて書き下す）


# 入力されたら、内容をpromptに格納(入力までは待機)
if prompt := st.chat_input("質問はありますか？"):
    # messagesにユーザーのプロンプトを追加
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ユーザーのアイコンで、promptをそのまま表示
    with st.chat_message("user"):
        st.markdown(prompt)

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

