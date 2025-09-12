import streamlit as st
import datetime
import uuid
from utils import validate_input, save_application, sidebar_style

# 記入年月日に使用する本日データ
today = datetime.date.today()

#=============================================申請ページ=========================================#

sidebar_style()

st.markdown(
            "<h1 style='text-align: center;'>三木市ふれあい収集利用申請</h1>",unsafe_allow_html=True
            )
col1, col2 = st.columns(2)
with col1:
    writing_day = st.text_input("記入年月日", value=today.strftime("%Y年-%m月-%d日"), disabled = True)
with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: right;'>※CM：ケアマネージャー</p>",
        unsafe_allow_html=True
        )

col1, col2 = st.columns(2)
with col1:
    st.markdown("-------------------------***申請者情報***-------------------------")
    address = st.text_area("住所", height=100)
    name = st.text_input("氏名（世帯の代表者）")
    birthday = st.date_input("生年月日",
                                value=None,
                                min_value=datetime.date(1900, 1, 1),
                                max_value=datetime.date.today(),
                                key = "input1")
    care_level = st.selectbox("要介護度",
                            ["選択してください","要介護1", "要介護2", "要介護3", "要介護4", "要介護5",
                            "区分2", "区分3", "区分4", "区分5", "区分6", "その他"])
    # 「その他」が選ばれたら、テキスト入力欄を表示
    if care_level == "その他":
        other_care_level = st.text_input("その他（例：要支援2など）")
    else:
        other_care_level = ""
    phone = st.text_input("電話番号")

with col2:
    st.markdown("----------------------***代行申請の場合***----------------------")
    agent = st.text_input("提出代行者氏名")
    relationship = st.selectbox("申請者との関係", ["選択してください","担当CM","親族等"])

    if relationship == "担当CM":
        info = st.text_input("続柄", value="ーーーーー", key = "input17", disabled=True)
    else:
        info = st.text_input("続柄", key = "input17")       

    st.markdown(
        "<p style='font-size:18px; margin-bottom:4px;'>-----介護事業所情報-----</p>",
        unsafe_allow_html=True
        )
    
    office_name = st.text_input("事業所名", key = "input16")

    col1, col2 = st.columns(2)
    with col1:
        office_phone = st.text_input("電話番号", key = "input12")
    with col2:
        if relationship == "担当CM":
            manager = st.text_input("担当CM", value="ーーーーー", disabled=True)
        else:
            manager = st.text_input("担当CM")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
        """
        <div style = "text-indent: 1em;">
        三木市ふれあい収集を利用したいため、三木市ふれあい収集実施要項第３条の規定により、
        関係書類を添えて下記のとおり申請します。<br>
        </div>
        <div style = "text-indent: 1em;">
        また、三木市ふれあい収集を申請するに当たり、利用決定及び利用開始後にふれあい収集を
        行うために必要な限度において、三木市が保有する私に関する個人情報を閲覧し、使用する
        ことに同意します。
        </div>
        """,
        unsafe_allow_html=True
        )
col1, col2, col3 = st.columns([4, 2, 4])
with col2:
    agree = st.checkbox("同意します")
st.write("")
st.markdown(
            """<h6 style='text-align: center;'>
            ------------------------------同居家族の状況・申請理由・緊急連絡先------------------------------
            </h6>""",
            unsafe_allow_html=True
            )

col1, col2 = st.columns(2)
with col1:
    st.markdown(
        "<p style='font-size:14px; margin-bottom:0;'>同居家族 1</p>",
        unsafe_allow_html=True
        )
    name_family1 = st.text_input("氏名", key = "input8")
    birthday_family1 = st.date_input("生年月日",
                                        value=None,
                                        min_value=datetime.date(1900, 1, 1),
                                        max_value=datetime.date.today(),
                                        key = "input2")
    relationship_1 = st.text_input("続柄", key = "input10")
    care_level_family1 = st.selectbox("要介護度",
                                        ["選択してください","要介護1", "要介護2", "要介護3","要介護4", "要介護5",
                                        "区分2", "区分3", "区分4", "区分5", "区分6", "その他"], key = "input3")
    if care_level_family1 == "その他":
        other_care_level_family1 = st.text_input("その他（例：要支援2など）", key = "input4")
    else:
        other_care_level_family1 = ""

with col2:
    st.markdown(
        "<p style='font-size:14px; margin-bottom:0;'>同居家族 2</p>",
        unsafe_allow_html=True
        )
    name_family2 = st.text_input("氏名", key = "input9")
    birthday_family2 = st.date_input("生年月日",
                                        value=None,
                                        min_value=datetime.date(1900, 1, 1),
                                        max_value=datetime.date.today(),
                                        key = "input5")
    relationship_2 = st.text_input("続柄", key = "input11")
    care_level_family2 = st.selectbox("要介護度",
                                        ["選択してください","要介護1", "要介護2", "要介護3","要介護4", "要介護5",
                                        "区分2", "区分3", "区分4", "区分5", "区分6", "その他"], key = "input6")
    if care_level_family2 == "その他":
        other_care_level_family2 = st.text_input("その他（例：要支援2など）", key = "input7")
    else:
        other_care_level_family2 = ""

reason = st.text_area("日常生活及び申請理由（200文字まで)",height=150, max_chars=200)

col1, col2 = st.columns(2)
with col1:
    call = st.selectbox("声かけ", ["選択してください", "希望する", "希望しない"])
with col2:
    st.markdown(
    """<p style='font-size:14px;'>※声かけ とは安否確認ではなく、収集に来たことを外からお伝えし、
    収集に来たことを知って安心していただくためのものです。</p>""",
    unsafe_allow_html=True
    )

st.markdown(
    "<p style='font-size:14px;margin-bottom:0; '>ご家族の緊急連絡先</p>",
    unsafe_allow_html=True
    )
col1, col2, col3 = st.columns(3)
with col1:
    emergency_name = st.text_input("氏名", key = "input13")
with col2:
    emergency_relationship = st.text_input("続柄", key = "input14")
with col3:
    emergency_phone = st.text_input("電話番号", key = "input15")

uploaded_files = st.file_uploader(
    "添付書類をアップロードしてください（PDF, JPG）",
    type = ["pdf", "jpg", "jpeg"],
    accept_multiple_files=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([4, 2, 4])
with col2:
    submit = st.button("送　　　信")

if submit:
    # ----- 受付番号の生成 -----
    reception_id = str(uuid.uuid4())[:8]

    # 入力データ辞書
    data = {
        "受付番号": reception_id,
        "記入年月日": writing_day,
        "住所": address,
        "氏名": name,
        "生年月日": birthday,
        "要介護度": care_level,
        "その他（例：要支援2など）": other_care_level,
        "電話番号": phone,
        "提出代行者氏名": agent,
        "申請者との関係": relationship,
        "続柄": info,
        "事業所名": office_name,
        "事業所電話": office_phone,
        "担当CM": manager,
        "個人情報の使用": "はい" if agree else "いいえ",
        "同居家族1_氏名": name_family1,
        "同居家族1_生年月日": birthday_family1.strftime("%Y-%m-%d") if birthday_family1 else "",
        "同居家族1_続柄": relationship_1,
        "同居家族1_要介護度": care_level_family1,
        "同居家族1_その他": other_care_level_family1,
        "同居家族2_氏名": name_family2,
        "同居家族2_生年月日": birthday_family2.strftime("%Y-%m-%d") if birthday_family2 else "",
        "同居家族2_続柄": relationship_2,
        "同居家族2_要介護度": care_level_family2,
        "同居家族2_その他": other_care_level_family2,
        "申請理由": reason,
        "声かけ": call,
        "緊急連絡先氏名": emergency_name,
        "緊急連絡先続柄": emergency_relationship,
        "緊急連絡先電話": emergency_phone,
        }
    
    # バリデーション関数のバリデーション（インプット、セレクトボックス、エリア）
    valid = validate_input(data, uploaded_files)

    # チェックボックスのバリデーション
    if not agree:
        st.error("申請には同意が必要です。チェックしてください。")
        valid = False

    if valid:
        save_application(data, uploaded_files, reception_id)

        st.success("送信が完了しました")
        st.info(f"受付番号：{reception_id}　を控えてください")

with col3:
    st.image("images/garbage10.png")