from openai import OpenAI
import streamlit as st
import datetime
import time

st.title("自動おしゃべりAI with 第三AI　v2")
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
# ヒント；あらゆるAI出力はpromptを前提にできる。会話させる場合でも、すべての出力の前に新たにpromptを追加できる。systemで役割を強制する必要はない。

# AI1（質問） and AI2（回答）
def generate_response(prompt, conversation_history):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation_history + [{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.7,
        #temperature=0.5,  # 回答の一貫性を高めるために温度を下げる
        stop=None,
    )
    return response.choices[0].message.content

# AI3（要約）
def summarize_conversation(conversation_history):
    # すべての会話履歴を一つの文字列に結合
    conversation_text = "\n".join([f"{entry['role']}: {entry['content']}" for entry in conversation_history])

    # AI_3による要約を生成
    summary_prompt = f"以下の会話内容を要約してください:\n{conversation_text}"
    summary_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": summary_prompt}],
        max_tokens=600,
        temperature=0.7  # 一貫性のある要約を得るために温度を調整
    )
    return summary_response.choices[0].message.content

def chat_between_gpts():
    # 初期設定
    conversation_history = []
    max_turns = st.sidebar.slider("Number of turns", min_value=1, max_value=10, value=3)
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
        ai2_prompt = f"以下の質問に具体的に答えてください: {ai1_response} ただし、あなたは質問に答えるだけであり、質問はしないでください。答えは簡潔にお願い。"
        ai2_response = generate_response(ai2_prompt, conversation_history)
        #ai2_response = generate_response(ai1_response, conversation_history)
        conversation_history.append({"role": "assistant", "content": ai2_response})
        st.write(f"**回答AI:** {ai2_response}")

        current_turn += 1
    
    # メインの会話が終了した後に、AI_3が要約を生成
    st.write("### 会話の要約")
    conversation_summary = summarize_conversation(conversation_history)
    st.write(conversation_summary)

chat_between_gpts()
