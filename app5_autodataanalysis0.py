import plotly.express as px
import streamlit as st
import pandas as pd
import fitz
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from openai import OpenAI
import time
import random

st.title("自動データ取得・可視化・AI分析")

def get_rand_wiki():
    # WikipediaのランダムなページのURL
    #random_url = "https://en.wikipedia.org/wiki/Special:Random"
    random_url = "https://ja.wikipedia.org/wiki/Special:Random"
    
    response = requests.get(random_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.find('h1', {'id': 'firstHeading'}).text
        content = soup.find('div', {'id': 'mw-content-text'}).text
        st.write(f"Title: {title}\n")
        #st.write(f"URL: {random_url}\n")
        st.write(f"Content: {content[:100]}...\n")  # 先頭の500文字を表示

        summary_wiki(content)
    else:
        st.write("Failed to retrieve the page")


def get_rand_page_from_category(category_url):
    # カテゴリーページのHTMLを取得
    response = requests.get(category_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')        
        
        # カテゴリーページ内のすべてのリンクを取得
        article_links = soup.select('div.mw-category-group a')        
        if article_links:
            # リンクのリストからランダムに1つ選択
            random_link = random.choice(article_links)['href']
            article_url = f"https://ja.wikipedia.org{random_link}"
            article_response = requests.get(article_url)
            if article_response.status_code == 200:
                article_soup = BeautifulSoup(article_response.text, 'html.parser')
                title = article_soup.find('h1', {'id': 'firstHeading'}).text
                content = article_soup.find('div', {'id': 'mw-content-text'}).text
                
                st.write(f"タイトル: {title}\n")
                #st.write(f"URL: {article_url}\n")
                st.write(f"内容: {content[:100]}...\n")  # 先頭の500文字を表示
                
                summary_wiki(content)
            else:
                st.write("記事の取得に失敗しました。")
        else:
            st.write("記事が見つかりませんでした。")
    else:
        st.write("カテゴリーページの取得に失敗しました。")

def summary_wiki(cont):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    data2 = cont
    # template
    template = '''
    あなたはwikipediaの記事全体を要約する専門家です。
    これから示す記事の内容を、重要なキーワードを用いて、簡潔に150字で要約してください。
    __MSG__
    '''
    template = template.replace('__MSG__', data2.replace('"', ''))    
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = [{'role': 'system', 'content': template}],
            stream = True,
        )
        response = st.write_stream(stream)

def pdf_plot_analysis_ai():
    # PDFからのテーブル取得と可視化：都道府県別コロナ定点観測の折れ線
    url = "https://www.mhlw.go.jp/stf/seisakunitsuite/bunya/0000121431_00461.html"
    response = requests.get(url)
    response.raise_for_status()  # エラーが発生した場合、例外を投げる
    
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")
    
    pdf_urls = [link.get("href") for link in links if link.get("href") and ".pdf" in link.get("href")]
    absolute_pdf_urls = [urljoin(url, pdf_url) for pdf_url in pdf_urls]
    latest_pdf_url = absolute_pdf_urls[0] if absolute_pdf_urls else None
    #st.write(f"最新のPDFのURL: {latest_pdf_url}")
    
    # 取得したPDFアドレスからテーブル取得
    url = latest_pdf_url
    response = requests.get(url)
    response.raise_for_status() # エラーになった時用
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
    #st.write(df.head())
    
    prefectures = df["都道府県"].unique().tolist()
    selected_prefecture = "京 都 府"
    #selected_prefecture = st.selectbox("都道府県を選択してください:", prefectures, index=prefectures.index("京 都 府"))
    prefecture_data = df[df["都道府県"] == selected_prefecture]
    prefecture_data = prefecture_data.melt(id_vars=["都道府県"], var_name="週", value_name="値").drop(columns="都道府県")
    fig = px.line(prefecture_data, x="週", y="値", title=f"{selected_prefecture}の週ごとのデータ")
    st.plotly_chart(fig)
    
    #### GPT part ####
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    #data1 = df[df['都道府県'] == '京 都 府']
    data1 = df[df['都道府県'] == selected_prefecture]
    data2 = data1.to_string()
    
    # template
    template = '''
    あなたは統計学の専門家です。
    これから示すデータは、直近の日本のコロナの定点観測あたりの感染者数のデータです。
    データを参照した上で、平均値を含めたデータ分析を行い、結果を解釈してください。できれば、今後の対策案も示してください。
    すべて結果を簡潔に短く100字で示して。
    __MSG__
    '''
    template = template.replace('__MSG__', data2.replace('"', ''))
    
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = [{'role': 'system', 'content': template}],
            stream = True,
        )
        response = st.write_stream(stream)

#### while part ####
running = st.button("開始")
stop = st.button("終了")
if running:
    loop_running = True    
    while loop_running:
        get_rand_wiki()
        category_url = "https://ja.wikipedia.org/wiki/Category:数学のエポニム"
        get_rand_page_from_category(category_url) 
        #pdf_plot_analysis_ai()
        time.sleep(3)        
        if stop:
            loop_running = False
            break

