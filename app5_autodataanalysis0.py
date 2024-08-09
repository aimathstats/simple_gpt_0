import plotly.express as px
import streamlit as st
import pandas as pd
import fitz
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from openai import OpenAI

st.title("自動データ取得・可視化・AI分析")

# PDFからのテーブル取得と可視化：都道府県別コロナ定点観測の折れ線
# 対象ページのURL
url = "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000121431_00461.html"
response = requests.get(url)
response.raise_for_status()  # エラーが発生した場合、例外を投げる

# BeautifulSoupでHTMLを解析
soup = BeautifulSoup(response.text, "html.parser")

# すべてのリンクを検索
links = soup.find_all("a")

# PDFファイルのURLを抽出
pdf_urls = [link.get("href") for link in links if link.get("href") and ".pdf" in link.get("href")]

# 相対URLを絶対URLに変換
absolute_pdf_urls = [urljoin(url, pdf_url) for pdf_url in pdf_urls]

# 最新のPDFのURLを取得
latest_pdf_url = absolute_pdf_urls[0] if absolute_pdf_urls else None
#latest_pdf_url = pdf_urls[0] if pdf_urls else None
st.write(f"最新のPDFのURL: {latest_pdf_url}")

# 取得したPDFアドレスからテーブル取得
#url = 'https://www.mhlw.go.jp/content/001282915.pdf'
url = latest_pdf_url
response = requests.get(url)
response.raise_for_status() # エラーになった時用

# ローカルにPDFファイルを保存
with open('covid.pdf', 'wb') as f:
    f.write(response.content) 

doc = fitz.open('covid.pdf', filetype="pdf")  
page_1 = doc[2]
pdf_text_1 = page_1.get_text("text")
tabs = page_1.find_tables()

table_data = tabs[0].extract()
columns0 = table_data[0] 
columns = table_data[1]
columns[0] = "都道府県" 
data_rows = table_data[2:]
df = pd.DataFrame(data_rows, columns=columns)
st.write(df)

prefectures = df["都道府県"].unique().tolist()
selected_prefecture = st.selectbox("都道府県を選択してください:", prefectures, index=prefectures.index("京 都 府"))
prefecture_data = df[df["都道府県"] == selected_prefecture]
prefecture_data = prefecture_data.melt(id_vars=["都道府県"], var_name="週", value_name="値").drop(columns="都道府県")

fig = px.line(prefecture_data, x="週", y="値", title=f"{selected_prefecture}の週ごとのデータ")
#st.subheader('2024年コロナ都道府県別定点観測:  ' + selected_prefecture)
st.plotly_chart(fig)



#### GPT part ####
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# data
#df = pd.read_csv('data/combined1.csv')
#st.write(df.columns[5])
data1 = df[df['都道府県'] == '京 都 府']
data2 = data1.to_string()

# template
template = '''
あなたは「統計学」の専門家です。

### 条件
- 全ての質問に対して、以下の詳細な「データ」を参照した上で、正確に答えてください。

### データ
"""__MSG__"""
'''

template = template.replace('__MSG__', data2.replace('"', ''))

# OpenAIのモデルを指定
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

# チャットの履歴 messages を初期化（一つ一つの messages は {role, content} の形式）
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages = [{'role': 'system', 'content': template}]

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

