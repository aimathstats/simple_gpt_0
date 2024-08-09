from openai import OpenAI
import streamlit as st
import pandas as pd
import os
import time

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
st.title("自動データ分析")

assistant = client.beta.assistants.create(
    name="汎用アシスタント",
    instructions="あなたは汎用的なアシスタントです。質問には簡潔かつ正確に答えてください。",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4o",
)
#assistant = client.beta.assistants.create(
#    name="Math Tutor",
#    instructions="You are a personal math tutor. Answer questions briefly, in a sentence or less.",
#    model="gpt-4o",
#)
ASSITANT_ID = assistant.id

def submit_message(thread, user_message, file=None, assistant_id= ASSITANT_ID):
    file_ids = submit_file(file)
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message, file_ids=file_ids
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

def submit_file(files):
    if files:
        ids = []
        for file_raw in files:
            file = client.files.create(
                file=file_raw,
                purpose='assistants'
            )
            ids.append(file.id)
        return ids
    else :
        return []

def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")

def create_thread_and_run(user_input,file=None):
    thread = client.beta.threads.create()
    run = submit_message(thread, user_input,file)
    return thread, run

def pretty_print(messages):
    for m in messages:
        with st.chat_message(m.role):
            for content in m.content:

                image_fileid = ""
                cont_dict = content.model_dump()
                if cont_dict.get("image_file") is not None:
                    image_fileid = cont_dict.get("image_file").get("file_id")
                    st.image(get_file(image_fileid))

                if cont_dict.get("text") is not None:
                    message_content = content.text
                    annotations = message_content.annotations
                    # citations = []
                    files = []
                    for index, annotation in enumerate(annotations):
                        message_content.value = message_content.value.replace(annotation.text, f' [{index}]')
                        if (file_path := getattr(annotation, 'file_path', None)):
                            cited_file = client.files.retrieve(file_path.file_id)
                            # citations.append(f'[{index}] Click <here> to download {cited_file.filename}, file_id: {file_path.file_id}')
                            files.append((file_path.file_id, annotation.text.split("/")[-1]))
                    # message_content.value += '\n' + '\n'.join(citations)
                    st.write(message_content.value)
                    for file in files:
                        st.download_button(
                            f"{file[1]} : ダウンロード",
                            get_file(file[0]),
                            file_name=file[1],
                        )

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

def get_file(file_id):
    retrieve_file = client.files.with_raw_response.retrieve_content(file_id)
    content = retrieve_file.content
    return content


####
with st.form("form", clear_on_submit=False):
    user_question = st.text_area("文章を入力")
    file = [st.file_uploader("ファイルをアップロード", accept_multiple_files=False)] or None
    submitted = st.form_submit_button("送信")

if submitted:
    if st.session_state.get("thread"):
        st.session_state["run"] = submit_message(st.session_state["thread"], user_question, file)
        st.session_state["run"] = wait_on_run(st.session_state["run"], st.session_state["thread"])
    else:
        st.session_state["thread"], st.session_state["run"] = create_thread_and_run(user_question, file)
        st.session_state["run"] = wait_on_run(st.session_state["run"], st.session_state["thread"])

if st.session_state.get("thread"):
    pretty_print(get_response(st.session_state["thread"]))



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

