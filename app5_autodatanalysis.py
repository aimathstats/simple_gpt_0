from openai import OpenAI
import streamlit as st
import pandas as pd

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("自動データ分析")
#st.subheader("統計学（前半）に関する質問に答えます")





# data
df = pd.read_csv('data/koukouseiseki.csv')
st.write(df["国語"])

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

