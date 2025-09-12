import streamlit as st
import datetime
import uuid
from utils import sidebar_style
from utils import validate_stop
from utils import save_stop

# 記入年月日に使用する本日データ
today = datetime.date.today()

#=====================================中止届ページ==============================================#

sidebar_style()

st.markdown(
            """<h1 style='text-align: center;'>
            三木市ふれあい収集利用中止届
            </h1>""",
            unsafe_allow_html=True
            )
st.subheader("")

col1, col2 = st.columns(2)
with col1:
    writing_day_s = st.text_input("記入年月日", value=today.strftime("%Y年-%m月-%d日"), disabled = True)
with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: right;'>※CM：ケアマネージャー</p>",
        unsafe_allow_html=True
        )

col1, col2 = st.columns(2)
with col1:
    st.markdown("-------------------------***申請者情報***-------------------------")
    s_address = st.text_area("住所", height=100)
    s_name = st.text_input("氏名")
with col2:
    st.markdown("----------------------***代行届出の場合***----------------------")
    s_agent = st.text_input("提出代行者氏名")
    s_relationship = st.selectbox("届出者との関係", ["選択してください","担当CM","親族等"])
    if s_relationship == "担当CM":
        s_office_name = st.text_input("事業所名")
        s_info = st.text_input("続柄", value="ーーーーー", disabled=True)
    elif s_relationship == "親族等":
        s_office_name = st.text_input("事業所名", value="ーーーーー", disabled=True)
        s_info = st.text_input("続柄")
    else:
        s_office_name = st.text_input("事業所名")
        s_info = st.text_input("続柄")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
        """
        <div style = "text-indent: 1em;">
        三木市ふれあい収集を中止したいので、三木市ふれあい収集実施要項第７条の規定により、<br>
        下記のとおり届け出ます。<br>
        </div>
        """,
        unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

s_reason = st.text_input("1　中止の理由")

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    restart_day = st.date_input("2　中止予定日",
                                value=None,
                                min_value=datetime.date(2011, 4, 1),
                                key="d_cyushi")


with col2:
    st.markdown("<h6></h6>から", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([4, 2, 4])
with col2:
    submit = st.button("送　　　信")

if submit:
    # ----- 受付番号 -----
    reception_id = str(uuid.uuid4())[:8]

    # ----- 入力データ辞書 -----
    data_s = {
            "受付番号": reception_id,
            "記入年月日": writing_day_s,
            "住所": s_address,
            "氏名": s_name,
            "提出代行者氏名": s_agent,
            "届出者との関係": s_relationship,
            "事業所名": s_office_name,
            "続柄": s_info,
            "中止の理由": s_reason,
            "中止予定日": restart_day
            }
    
    
    if validate_stop(data_s):
        save_stop(data_s, reception_id)
        st.success("送信が完了しました")
        st.info(f"受付番号：{reception_id}　を控えてください。")

with col3:
    st.image("images/garbage10.png")
