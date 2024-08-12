from openai import OpenAI
import streamlit as st

# OpenAIクライアントを初期化
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_response(role, prompt, conversation_history):
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=conversation_history + [{"role": "user", "content": prompt}],
        max_tokens=1000,
        temperature=0.7
    )
    return response.choices[0].message.content

def ai_2_task(conversation_history):
    prompt = "日本国内で2泊3日で訪れたい旅行先の候補を5つ挙げてください。出発地は京都です。"
    response = generate_response("AI_2", prompt, conversation_history)
    conversation_history.append({"role": "assistant", "content": response})
    st.write(f"**AI_2:** {response}")
    return response

def ai_3_task(ai_2_response, conversation_history):
    prompt = f"AI_2が挙げた旅行先候補: {ai_2_response}。この中から3つに絞り、さらに旅行プランを洗練させてください。"
    response = generate_response("AI_3", prompt, conversation_history)
    conversation_history.append({"role": "assistant", "content": response})
    st.write(f"**AI_3:** {response}")
    return response

def ai_4_task(ai_3_response, conversation_history):
    prompt = f"AI_3が選んだ旅行先候補: {ai_3_response}。それぞれのプランについて、旅行費用を概算してください。"
    response = generate_response("AI_4", prompt, conversation_history)
    conversation_history.append({"role": "assistant", "content": response})
    st.write(f"**AI_4:** {response}")
    return response

def ai_5_task(ai_4_response, conversation_history):
    prompt = f"AI_4が計算した旅行費用: {ai_4_response}。費用計算に間違いがないかを検証し、必要ならば再計算してください。"
    response = generate_response("AI_5", prompt, conversation_history)
    conversation_history.append({"role": "assistant", "content": response})
    st.write(f"**AI_5:** {response}")
    return response

def iterate_conversation_ai_2_ai_3(conversation_history, num_iterations):
    #ai_2_response = ai_2_task(conversation_history)
    for i in range(num_iterations):
        st.write(f"**ペアAの対話 - ラウンド {i+1}**")
        ai_2_response = ai_2_task(conversation_history) # add
        ai_3_response = ai_3_task(ai_2_response, conversation_history)
        #ai_2_response = ai_2_task(conversation_history)
    return ai_3_response

def iterate_conversation_ai_4_ai_5(conversation_history, ai_3_response, num_iterations):
    #ai_4_response = ai_4_task(ai_3_response, conversation_history)
    for i in range(num_iterations):
        st.write(f"**ペアBの対話 - ラウンド {i+1}**")
        ai_4_response = ai_4_task(ai_3_response, conversation_history) # add
        ai_5_response = ai_5_task(ai_4_response, conversation_history)
        #ai_4_response = ai_4_task(ai_3_response, conversation_history)
    return ai_5_response

def leader_task(conversation_history):
    prompt = "ペアAとペアBの会話と結果を基に、最も費用が低くなるプランを決定してください。"
    response = generate_response("リーダー", prompt, conversation_history)
    #st.write(f"**リーダー:** {response}")
    return response

def run_project():
    st.title("5者AIによる自動共同研究")

    # 会話履歴を保持
    conversation_history = []

    # 対話の繰り返し回数を選択するスライダー
    num_iterations = st.sidebar.slider("対話の繰り返し回数", min_value=1, max_value=5, value=2)

    # ペアAのタスク
    st.subheader("ペアAの活動")
    ai_3_response = iterate_conversation_ai_2_ai_3(conversation_history, num_iterations)

    # ペアBのタスク
    st.subheader("ペアBの活動")
    ai_5_response = iterate_conversation_ai_4_ai_5(conversation_history, ai_3_response, num_iterations)

    # リーダーの最終決定
    st.subheader("リーダーの最終決定")
    final_decision = leader_task(conversation_history)
    st.write(final_decision)

# Streamlitアプリケーションの実行
run_project()
