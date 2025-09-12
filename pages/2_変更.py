import streamlit as st
import datetime
import uuid
from utils import sidebar_style
from utils import validate_change 
from utils import save_change

# 記入年月日に使用する本日データ
today = datetime.date.today()

#=============================================変更届ページ============================================#

sidebar_style()

st.markdown(
            """<h1 style='text-align: center;'>
            三木市ふれあい収集<br>
            利用変更（一時停止・変更）届
            </h1>""",
            unsafe_allow_html=True
            )
st.subheader("")

col1, col2 = st.columns(2)
with col1:
    writing_day_c = st.text_input("記入年月日", value=today.strftime("%Y年-%m月-%d日"), disabled = True)
with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: right;'>※CM：ケアマネージャー</p>",
        unsafe_allow_html=True
        )

col1, col2 = st.columns(2)
with col1:
    st.markdown("-------------------------***申請者情報***-------------------------")
    c_address = st.text_area("住所", height=100)
    c_name = st.text_input("氏名")
with col2:
    st.markdown("----------------------***代行届出の場合***----------------------")
    c_agent = st.text_input("提出代行者氏名")
    c_relationship = st.selectbox("届出者との関係", ["選択してください","担当CM","親族等"])
    if c_relationship == "担当CM":
        c_office_name = st.text_input("事業所名")
        c_info = st.text_input("続柄", value="ーーーーー", disabled=True)
    elif c_relationship == "親族等":
        c_office_name = st.text_input("事業所名", value="ーーーーー", disabled=True)
        c_info = st.text_input("続柄")
    else:
        c_office_name = st.text_input("事業所名")
        c_info = st.text_input("続柄")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
        """
        <div style = "text-indent: 1em;">
        三木市ふれあい収集を（一時停止・再開）したいので、三木市ふれあい収集実施要項第６条の<br>
        規定により、下記のとおり届け出ます。<br>
        </div>
        """,
        unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    stop_restart = st.selectbox("1　一時停止・再開の別", ["選択してください", "一時停止", "再開"])

st.markdown("<br>", unsafe_allow_html=True)

c_reason = st.text_input("2　一時停止・再開の理由")

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    restart_day = st.date_input("3　一時停止・再開予定日",
                                value=None,
                                min_value=datetime.date(2011, 4, 1),
                                key="c_henkou")
with col2:
    st.markdown("<h6></h6>から", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([4, 2, 4])
with col2:
    submit = st.button("送　　　信")

if submit:
    # ----- 受付番号生成 -----
    reception_id = str(uuid.uuid4())[:8]

    # -----入力データ辞書---------
    data_c = {
            "受付番号": reception_id,
            "記入年月日": writing_day_c,
            "住所": c_address,
            "氏名": c_name,
            "提出代行者氏名": c_agent,
            "届出者との関係": c_relationship,
            "事業所名": c_office_name,
            "続柄": c_info,
            "一時停止・再開の別": stop_restart,
            "一時停止・再開の理由": c_reason,
            "一時停止・再開予定日": restart_day,
            }
    
    if validate_change(data_c):
        save_change(data_c, reception_id)
        st.success("送信が完了しました")
        st.info(f"受付番号：{reception_id}　を控えてください")

with col3:
    st.image("images/garbage10.png")