from openai import OpenAI
import streamlit as st
import datetime
import time

st.title("自動おしゃべりAI　v2")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_response(prompt, conversation_history):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history + [{"role": "user", "content": prompt}],
        max_tokens=200,
        #temperature=0.7,
        temperature=0.5,  # 回答の一貫性を高めるために温度を下げる
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
            ai1_prompt = "こんにちわ！会話を始めるために質問してください。なお挨拶は不要です。"
        else:
            ai1_prompt = "これまでの会話に基づき、別の質問をしてください。なお挨拶は不要です。"

        ai1_response = generate_response(ai1_prompt, conversation_history)
        conversation_history.append({"role": "assistant", "content": ai1_response})
        st.write(f"**質問AI:** {ai1_response}")

        # AI_2が質問に回答
        ai2_prompt = f"以下の質問に具体的に答えてください: {ai1_response} ただし、あなたは質問に答えるだけであり、あなたから質問をしないでください。答えは簡潔にお願い。"
        ai2_response = generate_response(ai2_prompt, conversation_history)
        #ai2_response = generate_response(ai1_response, conversation_history)
        conversation_history.append({"role": "assistant", "content": ai2_response})
        st.write(f"**回答AI:** {ai2_response}")

        current_turn += 1

chat_between_gpts()
