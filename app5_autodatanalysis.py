from openai import OpenAI
import streamlit as st
import pandas as pd
import os
import time

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.title("自動データ分析")
        
assistant = client.beta.assistants.create(
    name="Math Tutor",
    instructions="You are a personal math tutor. Write and run code to answer math questions.",
    model="gpt-4o",
    tools=[{"type": "code_interpreter"}]
)

thread = client.beta.threads.create()

user_question = st.text_input("ユーザーの質問を入力してください")

message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_question
)

run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
)

run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
)
                
time.sleep(30)
print(run.status)

messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            order="asc"
)

for message in messages:
    st.write(f"{message.role}: {message.content[0].text.value}")


#assistant = client.beta.assistants.create(
#    name="汎用アシスタント",
#    instructions="あなたは汎用的なアシスタントです。質問には簡潔かつ正確に答えてください。",
#    tools=[{"type": "code_interpreter"}],
#    model="gpt-4o",
#)
#ASSITANT_ID = assistant.id
#
#with st.form("form", clear_on_submit=False):
#    user_question = st.text_area("文章を入力")
#    file = [st.file_uploader("ファイルをアップロード", accept_multiple_files=False)] or None
#    submitted = st.form_submit_button("送信")
#
#if submitted:
#    if st.session_state.get("thread"):
#        st.session_state["run"] = submit_message(st.session_state["thread"], user_question, file)
#        st.session_state["run"] = wait_on_run(st.session_state["run"], st.session_state["thread"])
#    else:
#        st.session_state["thread"], st.session_state["run"] = create_thread_and_run(user_question, file)
#        st.session_state["run"] = wait_on_run(st.session_state["run"], st.session_state["thread"])
#
#if st.session_state.get("thread"):
#    pretty_print(get_response(st.session_state["thread"]))



# data
#df = pd.read_csv('data/koukouseiseki.csv')
#st.write(df["国語"])

# Upload a file with an "assistants" purpose
#file = client.files.create(
#  file=open("data/koukouseiseki.csv", "rb"),
#  purpose='assistants'
#)

# Create an assistant using the file ID
#assistant = client.beta.assistants.create(
#  instructions="あなたはデータ分析の教員です。データと質問が与えられたら、適切なコードを書いて。",
#  model="gpt-4o",
#  tools=[{"type": "code_interpreter"}],
#  tool_resources={
#    "code_interpreter": {
#      "file_ids": [file.id]
#    }
#  }
#)

#thread = client.beta.threads.create(
#  messages=[
#    {
#      "role": "user",
#      "content": "このデータの基本統計量を教えて。すべて日本語の文章として生成して。",
#      "attachments": [
#        {
#          "file_id": file.id,
#          "tools": [{"type": "code_interpreter"}]
#        }
#      ]
#    }
#  ]
#)
#st.markdown(thread)

