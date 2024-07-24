from openai import OpenAI
import streamlit as st

st.title("癒し系恋人AI")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


# OpenAIのモデルを指定
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# チャットの履歴 messages を初期化（一つ一つの messages は {role, content} の形式）
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages = [{'role': 'system', 'content': 'あなたは心優しい癒やし系の女性の24歳の恋人です。'}]


# それまでのメッセージを全て表示したままにする（このloopがないと、同じ場所を更新しながら会話が続く）
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"]) # 表示する（一瞬ですべて書き下す）


# 入力されたら、内容をpromptに格納(入力までは待機)
if prompt := st.chat_input("どうしたの？"):
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
            temperature = 1.5,
        )
        # AIの返答を流れるように出力
        response = st.write_stream(stream)
    
    # messagesにAIの返答を格納
    st.session_state.messages.append({"role": "assistant", "content": response})
    #　ここで一旦終わり、入力待機となる



