from openai import OpenAI
import streamlit as st
import pandas as pd

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("自動データ分析")
#st.subheader("統計学（前半）に関する質問に答えます")

# data
df = pd.read_csv('data/koukouseiseki.csv')
data1 = df["国語"]
st.write(data1)

# template
template = '''
あなたは大学経済学部の2年次開講科目「統計学」を担当する大学教員です。

"""__MSG__"""
'''

template = template.replace('__MSG__', data1.replace('"', ''))

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages = [{'role': 'system', 'content': template}]

# それまでのメッセージを全て表示したままにする（このloopがないと、同じ場所を更新しながら会話が続く）
#for message in st.session_state.messages[1:]:
#    with st.chat_message(message["role"]):
#        st.markdown(message["content"]) # 表示する（一瞬ですべて書き下す）

# 入力されたら、内容をpromptに格納(入力までは待機)
if prompt := st.chat_input("質問はありますか？"):
    # messagesにユーザーのプロンプトを追加
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ユーザーのアイコンで、promptをそのまま表示
    with st.chat_message("user"):
        st.markdown(prompt)

    # AIのアイコンで
    with st.chat_message("assistant"):
        # ChatGPTの返答をstreamに格納
        stream = client.chat.completions.create(
            model = st.session_state["openai_model"],
            # 会話履歴をすべて参照して渡す
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream = True,
            temperature = 0.5,
        )
        # AIの返答を流れるように出力
        response = st.write_stream(stream)
    
    # messagesにAIの返答を格納
    st.session_state.messages.append({"role": "assistant", "content": response})
    #　ここで一旦終わり、入力待機となる
