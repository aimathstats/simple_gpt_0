from openai import OpenAI
import streamlit as st

st.title("ChatGPT-like clone (2025)")

# OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 2025年の無難なデフォルト（必要に応じて変更）
# 例: "gpt-4o", "gpt-4o-mini" など
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

if "messages" not in st.session_state:
    st.session_state.messages = []

# 既存ログの表示
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

def stream_response(messages, model: str):
    """
    OpenAI Responses API のストリーミングを Streamlit の write_stream 向けに変換する。
    """
    # Responses API は input に「メッセージ配列」も渡せます（contentは文字列でOK）
    stream = client.responses.create(
        model=model,
        input=[{"role": m["role"], "content": m["content"]} for m in messages],
        stream=True,
    )

    # 公式イベント: response.output_text.delta の delta が増分テキスト :contentReference[oaicite:2]{index=2}
    for event in stream:
        # SDKのイベントは属性アクセスできる想定だが、念のため両対応
        event_type = getattr(event, "type", None) or event.get("type")
        if event_type == "response.output_text.delta":
            delta = getattr(event, "delta", None) or event.get("delta", "")
            if delta:
                yield delta

# 入力
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_text = st.write_stream(
            stream_response(st.session_state.messages, st.session_state["openai_model"])
        )

    st.session_state.messages.append({"role": "assistant", "content": response_text})

"""
from openai import OpenAI
import streamlit as st

st.title("ChatGPT-like clone")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
"""
