import plotly.express as px
import streamlit as st
import pandas as pd
import fitz
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from openai import OpenAI
import time

st.title("自動データ取得・可視化・AI分析")

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
    データを参照した上で、平均値を含めたデータ分析を行い、結果を解釈してください。
    できれば、今後の対策案も示してください。
    __MSG__
    '''
    template = template.replace('__MSG__', data2.replace('"', ''))
    
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o-mini"
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages = [{'role': 'system', 'content': template}]
    
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model = st.session_state["openai_model"],
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream = True,
            temperature = 0.5,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # 追加入力されたら、内容をpromptに格納(入力までは待機)
    #if prompt := st.chat_input("質問はありますか？"):
    #    st.session_state.messages.append({"role": "user", "content": prompt})
    #    with st.chat_message("user"):
    #        st.markdown(prompt)
    #    with st.chat_message("assistant"):
    #        stream = client.chat.completions.create(
    #            model = st.session_state["openai_model"],
    #            messages = [
    #                {"role": m["role"], "content": m["content"]}
    #                for m in st.session_state.messages
    #            ],
    #            stream = True,
    #            temperature = 0.5,
    #        )
    #        response = st.write_stream(stream)   
    #    st.session_state.messages.append({"role": "assistant", "content": response})


#### while part ####
running = st.button("開始")
stop = st.button("終了")

if running:
    loop_running = True    
    while loop_running:
        pdf_plot_analysis_ai()
        #if url:
        #    text = get_and_process_pdf(url)
        #    if text:
        #        visualize_data(text)
        #        summary = generate_summary(text)
        #        st.write(summary)
        time.sleep(20)
        if stop:
            loop_running = False
            st.write("終了しました。")
            break

