from openai import OpenAI
import streamlit as st
import pandas as pd

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("パウパトAI")
st.subheader("パウパトについて何でも聞いてみよう！")


############################################################################
# 画像のパス
background_image = 'data/paw_figure1.png'

# カスタムCSSを使って背景画像を設定
page_bg_img = f'''
<style>
.stApp {{
background-image: url("data:image/jpg;base64,{st.get_image_base64(background_image)}");
background-size: cover;
background-repeat: no-repeat;
background-attachment: fixed;
}}
</style>
'''

st.markdown(page_bg_img, unsafe_allow_html=True)

# サンプルのタイトルとテキスト
st.title("Background Image Example")
st.write("このStreamlitアプリの背景に画像が設定されています。")

# 画像をBase64エンコードする関数
def get_image_base64(image_path):
    import base64
    with open(image_path, 'rb') as img_file:
        b64_string = base64.b64encode(img_file.read()).decode('utf-8')
    return b64_string
############################################################################

# data
df = pd.read_csv('data/combined2.csv')
data1 = df["説明"]
#data1 = df["説明"][0:10]
data2 = data1.to_string()
#st.markdown(df.head())

# template
template = '''
あなたは○○です。

### 条件
- 全ての質問に対して、講義内容に関する以下の詳細な「授業資料」を参照した上で、正確に答えてください。

### 授業資料
"""__MSG__"""
'''

template = template.replace('__MSG__', data2.replace('"', ''))

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
    
    # messagesにAIの返答を格納
    st.session_state.messages.append({"role": "assistant", "content": response})
    #　ここで一旦終わり、入力待機となる

