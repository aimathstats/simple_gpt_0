# 5者AI generated by ChatGPT 4o at 2024/08/12

from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_response(role, prompt, conversation_history):
    response = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=conversation_history + [{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content

def ai_2_task(conversation_history):
    prompt = "日本国内で1泊2日で訪れたい旅行先の候補を4つ挙げてください。出発地は京都です。人数は大人2名です。ただし、50字以内で出力して。"
    response = generate_response("AI_2", prompt, conversation_history)
    conversation_history.append({"role": "assistant", "content": response})
    st.write(f"**AI_2（列挙役）:** {response}")
    return response

def ai_3_task(ai_2_response, conversation_history):
    prompt = f"AI_2が挙げた旅行先候補: {ai_2_response}。この中から2つに絞り、さらに旅行プランを洗練させてください。ただし、50字以内で出力して。"
    response = generate_response("AI_3", prompt, conversation_history)
    conversation_history.append({"role": "assistant", "content": response})
    st.write(f"**AI_3（選抜役）:** {response}")
    return response

def ai_4_task(ai_3_response, conversation_history):
    prompt = f"AI_3が選んだ旅行先候補: {ai_3_response}。それぞれのプランについて、旅行費用を概算してください。ただし、50字以内で出力して。"
    response = generate_response("AI_4", prompt, conversation_history)
    conversation_history.append({"role": "assistant", "content": response})
    st.write(f"**AI_4（試算役）:** {response}")
    return response

def ai_5_task(ai_4_response, conversation_history):
    prompt = f"AI_4が計算した旅行費用: {ai_4_response}。費用計算に間違いがないかを検証し、必要ならば再計算してください。ただし、50字以内で出力して。"
    response = generate_response("AI_5", prompt, conversation_history)
    conversation_history.append({"role": "assistant", "content": response})
    st.write(f"**AI_5（検証役）:** {response}")
    return response

def iterate_conversation_ai2_ai3(conversation_history, num_iterations):
    for i in range(num_iterations):
        st.write(f"**ペアAの対話 - ラウンド {i+1}**")
        ai_2_response = ai_2_task(conversation_history)
        ai_3_response = ai_3_task(ai_2_response, conversation_history)
    return ai_3_response

def iterate_conversation_ai4_ai5(conversation_history, ai_3_response, num_iterations):
    for i in range(num_iterations):
        st.write(f"**ペアBの対話 - ラウンド {i+1}**")
        ai_4_response = ai_4_task(ai_3_response, conversation_history)
        ai_5_response = ai_5_task(ai_4_response, conversation_history)
    return ai_5_response

def leader_task(conversation_history):
    prompt = "あなたはリーダーとして、これまでの会話と結果を基に魅力的でかつ最も費用が低くなるプランを決定してください。ただし、会話履歴にない情報は使わないで。"
    response = generate_response("リーダー", prompt, conversation_history)
    #st.write(f"**リーダー:** {response}")
    return response

def run_project():
    st.title("5者AI自動共同研究")
    conversation_history = []
    num_iterations = st.sidebar.slider("対話の繰り返し回数", min_value=1, max_value=5, value=2)

    st.subheader("ペアAの活動")
    ai_3_response = iterate_conversation_ai2_ai3(conversation_history, num_iterations)
    st.subheader("ペアBの活動")
    ai_5_response = iterate_conversation_ai4_ai5(conversation_history, ai_3_response, num_iterations)
    
    st.subheader("リーダーの決定")
    st.write(leader_task(conversation_history))

run_project()
