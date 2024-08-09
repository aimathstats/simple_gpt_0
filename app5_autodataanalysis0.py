import plotly.express as px
import streamlit as st
import numpy as np
import pandas as pd
import fitz
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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
