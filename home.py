import streamlit as st
from utils import sidebar_style

#===========================================ホーム画面=========================================#

sidebar_style()

st.set_page_config(page_title="ふれあい収集", page_icon="images/favi_keitora.png")

st.markdown(
                """<h1 style='text-align: center;'>
                三木市ふれあい収集 利用<br>
                ［申請・変更・中止］フォーム
                </h1>""",
                unsafe_allow_html=True
                )

col1, col2 = st.columns([3, 1])
with col2:
    st.image("images/keitora.png", width=500)

st.markdown("""
    <div style= "font-size:18px">
    ようこそ。<br>
    左のサイドバーから申請・変更・中止のページに移動できます。<br><br>
    申請・・・新規申請の方または継続申請の方<br>
    変更・・・現在ふれあい収集をご利用の方で一時停止や再開をしたい方<br>
    中止・・・現在ふれあい収集をご利用の方でサービスの中止をしたい方
    </div>""",
    unsafe_allow_html=True    
    )

