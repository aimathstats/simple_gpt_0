from openai import OpenAI
import streamlit as st
import datetime
import time

st.title("ChatGPT-like clone")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# new codes
if "messages2" not in st.session_state:
    st.session_state.messages2 = []

template = '''
あなたは質問者です。
相手の返答に対して、必ず何か質問してください。
質問内容は何でもいいですが、一般的で答えるのが簡単なものにして下さい。
質問は簡潔に一文でお願いします。
'''

#prompt = st.chat_input("質問？")
prompt = "こんにちわ"
response = False

#endtime = datetime.datetime.now() + datetime.timedelta(seconds=int(10))
#while datetime.datetime.now() < endtime:
#    time.sleep(2)
#    #prompt = "こんにちわ"

if prompt:
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

if response:
    with st.chat_message("user"):
        stream2 = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": "system", "content": template},
                {"role": "user", "content": response}
            ],
            stream=True,
        )
        prompt = st.write_stream(stream2)
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
