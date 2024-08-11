from openai import OpenAI
import streamlit as st
import datetime
import time

st.title("自動おしゃべりAI")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

template_system = '''
あなたは質問AIに対して回答する、回答AIです。
相手からの返答（質問）に対して、必ず何か回答してください。
内容は簡潔に一文でお願いします。
なお、あなたから質問はしないでください。
相手は仲のよい友人ですので挨拶は一切不要です。
'''

template_user = '''
あなたは回答AIに対して質問する、質問AIです。
相手の返答に対して、必ず何か質問してください。
質問内容は何でもいいですが、答えるのが簡単なものにして下さい。
質問は簡潔に一文でお願いします。
相手は仲のよい友人ですので挨拶は一切不要です。
'''

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages = [{'role': 'system', 'content': template_system}]

for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = "こんにちは！日本のJ-POPについて話しませんか？"
st.session_state.messages.append({"role": "user", "content": prompt})
with st.chat_message("user"):
    st.markdown(prompt)

endtime = datetime.datetime.now() + datetime.timedelta(seconds=int(40))

while datetime.datetime.now() < endtime:
    time.sleep(1)
    with st.chat_message("assistant"): #返答
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
            temperature = 1.0,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

    time.sleep(1)
    with st.chat_message("user"): #質問
        stream2 = client.chat.completions.create(
            model=st.session_state["openai_model"],
            #messages=[
            #    {"role": m["role"], "content": m["content"]}
            #    for m in st.session_state.messages
            #],
            messages=[
                {"role": "system", "content": template_user},
                {"role": "user", "content": response}
            ],
            stream=True,
            temperature = 3.0,
        )
        prompt2 = st.write_stream(stream2)
    st.session_state.messages.append({"role": "user", "content": prompt2})

