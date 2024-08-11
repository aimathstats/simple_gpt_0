import openai
import streamlit as st

# OpenAI APIキーを設定
openai.api_key = "YOUR_API_KEY"

def generate_response(prompt, conversation_history):
    response = openai.ChatCompletion.create(
        model="gpt-4",  # GPT-4モデルを使用
        messages=conversation_history + [{"role": "user", "content": prompt}],
        max_tokens=150,
        temperature=0.7,
        stop=None,
    )
    return response.choices[0].message["content"]

def chat_between_gpts():
    # 初期設定
    conversation_history = []
    max_turns = st.sidebar.slider("Number of turns", min_value=1, max_value=10, value=5)
    current_turn = 1

    while current_turn <= max_turns:
        # AI 1が質問を生成
        if current_turn == 1:
            ai1_prompt = "Hello, can you ask me a question to start our conversation?"
        else:
            ai1_prompt = "Can you ask me another question based on our conversation?"

        ai1_response = generate_response(ai1_prompt, conversation_history)
        conversation_history.append({"role": "assistant", "content": ai1_response})

        st.write(f"**GPT-1:** {ai1_response}")

        # AI 2が質問に回答
        ai2_response = generate_response(ai1_response, conversation_history)
        conversation_history.append({"role": "assistant", "content": ai2_response})

        st.write(f"**GPT-2:** {ai2_response}")

        current_turn += 1

st.title("GPT to GPT Conversation")
chat_between_gpts()
