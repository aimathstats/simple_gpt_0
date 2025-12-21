from openai import OpenAI
import streamlit as st

st.title("ChatGPT-like clone")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    #st.session_state["openai_model"] = "gpt-3.5-turbo"
    st.session_state["openai_model"] = "gpt-4o-mini"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    #### old code (chat.completions.create)
    #with st.chat_message("assistant"):
    #    stream = client.chat.completions.create(
    #        model=st.session_state["openai_model"],
    #        messages=[
    #            {"role": m["role"], "content": m["content"]}
    #            for m in st.session_state.messages
    #        ],
    #        stream=True,
    #    )
    #    response = st.write_stream(stream)

    ##### new code for responses API without stream output (2025/12/21)
    #with st.chat_message("assistant"):
    #    r = client.responses.create(
    #        model=st.session_state["openai_model"],
    #        input=[
    #            {"role": m["role"], "content": m["content"]}
    #            for m in st.session_state.messages
    #        ],
    #    )
    #    response = r.output_text  # 生成された最終テキスト
    #    st.markdown(response)
    ##### stream (25/12/21)
    def response_stream():
        stream = client.responses.create(
            model=st.session_state["openai_model"],
            input=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        for event in stream:
            etype = getattr(event, "type", None) or event.get("type")
            if etype == "response.output_text.delta":
                delta = getattr(event, "delta", None) or event.get("delta", "")
                if delta:
                    yield delta

    with st.chat_message("assistant"):
        response = st.write_stream(response_stream())
    ####
  
    st.session_state.messages.append({"role": "assistant", "content": response})

