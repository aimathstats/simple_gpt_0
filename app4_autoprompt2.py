from openai import OpenAI
import streamlit as st
import datetime
import time

# OpenAI APIキーを設定
#openai.api_key = "YOUR_API_KEY"
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_response(prompt, conversation_history):
    response = client.chat.completions.create(
    #response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=conversation_history + [{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.7,
        stop=None,
    )
    return response.choices[0].message.content

def chat_between_gpts():
    # 初期設定
    conversation_history = []
    max_turns = st.sidebar.slider("Number of turns", min_value=1, max_value=10, value=5)
    current_turn = 1

    while current_turn <= max_turns:
        # AI_1が質問を生成
        if current_turn == 1:
            ai1_prompt = "こんにちわ！会話を始めるために質問してくれる？なお、挨拶は一切不要です。"
        else:
            ai1_prompt = "私たちの会話に基づいて、別の質問をしてください。なお、挨拶は一切不要です。"

        ai1_response = generate_response(ai1_prompt, conversation_history)
        conversation_history.append({"role": "assistant", "content": ai1_response})
        st.write(f"**AI-1（質問者）:** {ai1_response}")

        # AI_2が質問に回答
        ai2_response = generate_response(ai1_response, conversation_history)
        conversation_history.append({"role": "assistant", "content": ai2_response})
        st.write(f"**AI-2（回答者）:** {ai2_response}")

        current_turn += 1

st.title("GPT to GPT Conversation")
chat_between_gpts()
