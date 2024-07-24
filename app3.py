import openai
from openai import OpenAI
import streamlit as st
import json

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


st.title("ももたろうゲーム")
st.subheader('犬を見つけました。仲間にしたいので説得しましょう', divider='rainbow')

template = '''
私は桃太郎であなたを仲間にしようと説得します。
鬼ヶ島へ鬼退治に行きたいのですが、仲間になってくれますか？

### 条件
- 仲間になるなら結果にtrueを、嫌ならfalseを返します。
- 説得内容に「きび団子」があれば{"結果": false, "理由":"食べ飽きている"}と返します。

### 応答の例
{"結果": false, "理由": "興味がないから"}
{"結果": true, "理由": "志に共感したため"}
{"結果": false, "理由": "きび団子になんかには釣られないよ"}

###説得内容
"""__MSG__"""
'''

#- 権力を手に入れられるのであれば、仲間になりやすいです。

# OpenAIのモデルを指定
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# チャットの履歴 messages を初期化（一つ一つの messages は {role, content} の形式）
if "messages" not in st.session_state:
    st.session_state.messages = []

def chat_completion(messages):
    response = openai.chat.completions.create(
        model = st.session_state["openai_model"],
        messages = messages)
    return response.choices[0].message.content


# 入力されたら、内容をpromptに格納(入力までは待機)
if prompt := st.chat_input("説得してください"):
    #　テンプレートの説得内容だけを更新
    prompt2 = template.replace('__MSG__', prompt.replace('"', ''))
    message = [
        {'role': 'system', 'content': 'あなたは強情な犬です。JSONで応答してください。'},
        {'role': 'user', 'content': prompt2}
    ]

    # ユーザーのアイコンで、promptをそのまま表示
    with st.chat_message("user"):
        st.markdown(prompt)

    # AIのアイコンで
    with st.chat_message("assistant"):
        res = {'結果': False, '理由': '不明'}
        s = chat_completion(message)
        #st.markdown(s)
        #s = client.chat.completions.create(
        #    model = st.session_state["openai_model"],
        #    messages = message,
        #)
        try:
            res = json.loads(s) # JSONデータを解析
        except:
            print('[エラー] JSONの解析に失敗しました。', s)
        
        # ChatGPTの応答を表示
        if ('結果' in res) and ('理由' in res) and (res['結果']):
            response = '犬は仲間になってくれました！理由は…' + res['理由'] + '。ゲームクリア！'
        else:
            reason = res['理由'] if '理由' in res else 'なし'
            response = '残念!犬に断られました。理由は、' + reason + '。引き続き説得しましょう。'
        st.markdown(response)



