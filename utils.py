import streamlit as st
import datetime
import csv
from pathlib import Path
from fpdf import FPDF


# ========================================ホームページ=======================================================

# ------------------------------------------サイドバースタイル-------------------------------------
def sidebar_style():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] *{ font-size: 20px; }

        [data-testid="stSidebarNav"] li { margin-bottom: 10px !important; }
        """,
        unsafe_allow_html=True
    )

# =======================================申請ページ==========================================================

# ------------------------------申請のバリデーション関数-------------------------------------------
def validate_input(data: dict, files: list) -> bool:
    input_errors = []
    file_errors = []

    # ----- 必須申請者項目 -----
    applicant_fields = [
                        "住所", "氏名", "生年月日", "要介護度", "電話番号", "申請理由", "声かけ",
                        "緊急連絡先氏名", "緊急連絡先続柄", "緊急連絡先電話"
                        ]
    for field in applicant_fields:
        if not data.get(field) or data.get(field) == "選択してください":
            input_errors.append(f"{field}")
    # -----「要介護度」で「その他」を選択されたあとの「"例：要支援2など"」を必須に -----
    if data.get("要介護度") == "その他" and not data.get("その他（例：要支援2など）"):
        input_errors.append("その他（例：要支援2など）")

    # ----- 添付ファイルチェック -----
    if len(files) < 2:
        file_errors.append("添付ファイル(介護保険被保険者証写・ヘルパー利用確認書類)をアップロードしてください")

    # ----- 代行申請チェック -----
    if data.get("提出代行者氏名"):
        for field in ["申請者との関係", "続柄", "事業所名", "事業所電話", "担当CM"]:
            if not data.get(field) or data.get(field) == "選択してください":
                input_errors.append(f"{field}")

    # -----同居家族チェック -----
    for i in [1, 2]:
        family_prefix = f"同居家族{i}"
        family_fields = [
            f"{family_prefix}氏名",
            f"{family_prefix}生年月日",
            f"{family_prefix}続柄",
            f"{family_prefix}要介護度"
        ]
        # ----- 1つでも入力があれば必須チェック -----
        if any(data.get(f) for f in family_fields):
            for f in family_fields:
                if not data.get(f) or data.get(f) == "選択してください":
                    input_errors.append(f"{f} が未入力です")
            # 「その他要介護度」が入力されている場合もチェック
            other_field = f"{family_prefix}その他要介護度"
            if data.get(f"{family_prefix}要介護度") == "その他" and not data.get(other_field):
                input_errors.append(f"{other_field} が未入力です")

    # ----- エラーまとめて表示 -----
    if input_errors:
        st.error(f"{" , ".join(input_errors)}を入力・選択してください")
    if file_errors:
        st.error(f"{"".join(file_errors)}")

    # ----- ここでFalseを返すことで素通りを防ぐ -----
    if input_errors or file_errors:
        return False

    return True

# --------------------------------------- 申請の保存処理関数 ----------------------------------------
def save_application(data: dict, files: list, reception_id):
    # ----- 保存先ベースフォルダを作る -----
    BASE_DIR = Path("1_shinsei")
    BASE_DIR.mkdir(exist_ok=True)

    # ----- フォルダ名を　氏名_記入年月日　にして作る -----
    folder_name = f"{data['氏名']}_{datetime.date.today().strftime('%Y%m%d')}"
    folder_path = BASE_DIR / folder_name
    folder_path.mkdir(exist_ok=True)

    # ----- csv保存 -----
    csv_file = folder_path / "info.csv"
    headers = list(data.keys())
    with open(csv_file, "w", newline="", encoding="cp932") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerow(data)
    
    # ----- 添付ファイル保存 -----
    for file in files:
        file_path = folder_path / file.name
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())

    # ::::::::::::::::::::::::::::::::::::: pdf保存 :::::::::::::::::::::::::::::::::::::
    pdf = FPDF(format="A4")
    pdf.add_page()

    # デフォルトの左右余白は 10mm
    pdf.set_left_margin(15)   # 左余白を 10mm → 15mm に
    pdf.set_right_margin(15)  # 右余白を 10mm → 15mm に
    pdf.set_top_margin(10)    # 上余白は必要に応じて

    # フォント設定
    font_path = Path(__file__).parent / "fonts" / "NotoSansJP-Regular.ttf"
    pdf.add_font("NotoSansJP", "", str(font_path), uni=True)

    # タイトル
    pdf.set_font("NotoSansJP", "", 16)
    pdf.cell(0, 12, "三木市ふれあい収集利用申請書", ln=1, align="C")
    
    # フォントを通常に戻す
    pdf.set_font("NotoSansJP", "", 11)
    pdf.cell(0, 12, f"記入年月日：{data['記入年月日']}", ln=1)
    pdf.ln(5)

    # ラインを全体に引く
    left_margin = 15
    right_margin = 15
    page_width = pdf.w - left_margin - right_margin
    y_1 = pdf.get_y()
    pdf.line(left_margin, y_1, left_margin + page_width, y_1)

    # ページ幅を考慮した列幅
    col_width = pdf.w / 2 - 15  # 左右列の幅
    line_height = 7  # 行の高さ

    # ===== 左列：申請者情報 =====
    pdf.set_xy(15, y_1+5)  # 左上の座標
    pdf.cell(col_width, line_height, "----------申請者情報----------", ln=1)
    pdf.cell(col_width, line_height, f"●氏名：{data['氏名']}", ln=1)
    pdf.cell(col_width, line_height, f"●生年月日：{data['生年月日']}", ln=1)
    pdf.cell(col_width, line_height, "●住所：", ln=1)
    pdf.multi_cell(col_width, line_height, f"{data['住所']}", ln=1)
    pdf.cell(col_width, line_height, f"●要介護度：{data['要介護度']}", ln=1)
    pdf.cell(col_width, line_height, f"●その他要介護度：{data['その他（例：要支援2など）']}", ln=1)
    pdf.cell(col_width, line_height, f"●電話番号：{data['電話番号']}", ln=1)
    pdf.ln(5)
    left_y = pdf.get_y()

    # ===== 右列：提出代行者情報 =====
    right_start_x = pdf.w/2 + 5
    pdf.set_xy(right_start_x, y_1+5)  # 右列開始位置
    pdf.cell(col_width, line_height, "----------代行申請の場合----------", ln=0)
    pdf.set_xy(right_start_x, y_1+5+line_height)
    pdf.cell(col_width, line_height, f"●提出代行者氏名：{data['提出代行者氏名']}", ln=0)
    pdf.set_xy(right_start_x, y_1+5+line_height*2)
    pdf.cell(col_width, line_height, f"●申請者との関係：{data['申請者との関係']}", ln=0)
    pdf.set_xy(right_start_x, y_1+5+line_height*3)
    pdf.cell(col_width, line_height, f"●続柄：{data['続柄']}", ln=0)
    pdf.set_xy(right_start_x, y_1+5+line_height*4)
    pdf.cell(col_width, line_height, f"●事業所名：{data['事業所名']}", ln=0)
    pdf.set_xy(right_start_x, y_1+5+line_height*5)
    pdf.cell(col_width, line_height, f"●電話番号：{data['事業所電話']}", ln=0)
    pdf.set_xy(right_start_x, y_1+5+line_height*6)
    pdf.cell(col_width, line_height, f"●担当CM：{data['担当CM']}", ln=1)
    pdf.ln(5)
    right_y = pdf.get_y()


    # ラインを全体に引く
    left_margin = 15
    right_margin = 15
    line_set_y = max(left_y, right_y)
    page_width = pdf.w - left_margin - right_margin
    pdf.line(left_margin, line_set_y, left_margin + page_width, line_set_y)

    pdf.ln(5)

    #　===== 左列：同居家族1情報 =====
    familyinfo_x = 15
    fmaliyinfo_y = line_set_y+5
    pdf.set_xy(familyinfo_x, fmaliyinfo_y)
    pdf.cell(col_width, line_height, "----------同居家族1----------", ln=1)
    pdf.cell(col_width, line_height, f"●氏名：{data['同居家族1_氏名']}", ln=1)
    pdf.cell(col_width, line_height, f"●生年月日：{data['同居家族1_生年月日']}", ln=1)
    pdf.cell(col_width, line_height, f"●続柄：{data['同居家族1_続柄']}", ln=1)
    pdf.cell(col_width, line_height, f"●要介護度：{data['同居家族1_要介護度']}", ln=1)
    pdf.cell(col_width, line_height, f"●その他要介護度：{data['同居家族1_その他']}", ln=1)

    # ===== 右列：同居家族2情報 =====
    pdf.set_xy(right_start_x, fmaliyinfo_y)
    pdf.cell(col_width, line_height, "----------同居家族2----------", ln=0)
    pdf.set_xy(right_start_x, fmaliyinfo_y+line_height)
    pdf.cell(col_width, line_height, f"●氏名：{data['同居家族2_氏名']}", ln=0)
    pdf.set_xy(right_start_x, fmaliyinfo_y+line_height*2)
    pdf.cell(col_width, line_height, f"●生年月日：{data['同居家族2_生年月日']}", ln=0)
    pdf.set_xy(right_start_x, fmaliyinfo_y+line_height*3)
    pdf.cell(col_width, line_height, f"●続柄：{data['同居家族2_続柄']}", ln=0)
    pdf.set_xy(right_start_x, fmaliyinfo_y+line_height*4)
    pdf.cell(col_width, line_height, f"●要介護度：{data['同居家族2_要介護度']}", ln=0)
    pdf.set_xy(right_start_x, fmaliyinfo_y+line_height*5)
    pdf.cell(col_width, line_height, f"●その他要介護度：{data['同居家族2_その他']}", ln=1)

    pdf.ln(5)

    pdf.line(left_margin, pdf.get_y(), left_margin + page_width, pdf.get_y())

    pdf.ln(5)

    pdf.cell(0, line_height, f"●個人情報の使用に関する同意：{data['個人情報の使用']}", ln=1)
    pdf.cell(0, line_height, f"●声かけ：{data['声かけ']}", ln=1)
    pdf.cell(0, line_height, "●申請理由", ln=1)
    pdf.set_xy(15, pdf.get_y())
    pdf.multi_cell(pdf.w - 30, 8, f"{data['申請理由']}", border=1)

    pdf.ln(5)

    pdf.line(left_margin, pdf.get_y(), left_margin + page_width, pdf.get_y())

    pdf.ln(5)

    pdf.cell(0, line_height, "----------ご家族の緊急連絡先----------", ln=1)
    pdf.cell(0, line_height, f"●氏名：{data['緊急連絡先氏名']}", ln=1)
    pdf.cell(0, line_height, f"●続柄：{data['緊急連絡先続柄']}", ln=1)
    pdf.cell(0, line_height, f"●電話番号：{data['緊急連絡先電話']}", ln=1)

    # PDF 保存
    pdf_file = folder_path / f"申請書({reception_id}).pdf"
    pdf.output(str(pdf_file))



# ========================================= 変更ページ =====================================================

# ----------------------------------変更のバリデーション関数--------------------------------------
def validate_change(data_c: dict):
    input_errors_c = []

    # ----- 必須入力項目チェック -----
    change_field = ["住所", "氏名", "一時停止・再開の別", "一時停止・再開の理由", "一時停止・再開予定日"]
    for field in change_field:
        if not data_c.get(field) or data_c.get(field) == "選択してください":
            input_errors_c.append(f"{field}")
    
    # ----- 代行届出チェック -----
    if data_c.get("提出代行者氏名"):
        for field in ["届出者との関係", "事業所名", "続柄"]:
            if not data_c.get(field) or data_c.get(field) == "選択してください":
                input_errors_c.append(f"{field}")
    
    # ----- エラー表示 -----
    if input_errors_c:
        st.error(f"{" , ".join(input_errors_c)}を入力・選択してください")
        return False
    
    return True

# ----- 変更の保存処理関数 -----
def save_change(data_c: dict, reception_id):
    # ----- 保存先ベースフォルダを作る -----
    BASE_DIC_C = Path("2_henkou")
    BASE_DIC_C.mkdir(exist_ok=True)

    # ----- フォルダ名を　名前_記入年月日　にして作る -----
    folder_name_c = f"{data_c["氏名"]}_{datetime.date.today().strftime("%Y%m%d")}"
    folder_path_c = BASE_DIC_C / folder_name_c
    folder_path_c.mkdir(exist_ok=True)

    # ----- csv保存 -----
    csv_file_c = folder_path_c / "info.csv"
    headers_c = list(data_c.keys())
    with open(csv_file_c, "w", newline="", encoding="cp932") as f:
        writer_c = csv.DictWriter(f, fieldnames=headers_c)
        writer_c.writeheader()
        writer_c.writerow(data_c)
    
    # ::::::::::::::::::::::::::::::::::::: pdf保存 :::::::::::::::::::::::::::::::::::::
    pdf = FPDF(format="A4")
    pdf.add_page()

    pdf.set_left_margin(15)   # 左余白を 10mm → 15mm に
    pdf.set_right_margin(15)  # 右余白を 10mm → 15mm に
    pdf.set_top_margin(10)    # 上余白は必要に応じて

    # フォント設定
    font_path = Path(__file__).parent / "fonts" / "NotoSansJP-Regular.ttf"
    pdf.add_font("NotoSansJP", "", str(font_path), uni=True)

    # タイトル
    pdf.set_font("NotoSansJP", "", 16)
    pdf.cell(0, 12, "三木市ふれあい収集利用変更届", ln=1, align="C")
    
    # フォントを通常に戻す
    pdf.set_font("NotoSansJP", "", 12)
    pdf.cell(0, 12, f"記入年月日：{data_c['記入年月日']}", ln=1)

    pdf.ln(5)
    y_2 = pdf.get_y()

     # ラインを全体に引く
    left_margin = 15
    right_margin = 15
    page_width = pdf.w - left_margin - right_margin
    pdf.line(left_margin, y_2, left_margin + page_width, y_2)

    pdf.ln(5)
    y_3 = pdf.get_y()

    # ページ幅を考慮した列幅
    col_width = pdf.w / 2 - 15  # 左右列の幅
    line_height = 9  # 行の高さ

    # ===== 左列：申請者情報 =====
    pdf.set_xy(15, y_3)  # 左上の座標
    pdf.cell(col_width, line_height, "----------申請者情報----------", ln=1)
    pdf.cell(col_width, line_height, f"●氏名：{data_c['氏名']}", ln=1)
    pdf.cell(col_width, line_height, "●住所：", ln=1)
    pdf.multi_cell(col_width, line_height, f"{data_c['住所']}", ln=1)
  
    left_y = pdf.get_y()

    # ===== 右列：提出代行者情報 =====
    right_start_x = pdf.w/2 + 5
    pdf.set_xy(right_start_x, y_3)  # 右列開始位置
    pdf.cell(col_width, line_height, "----------代行届出の場合----------", ln=0)
    pdf.set_xy(right_start_x, y_3+line_height)
    pdf.cell(col_width, line_height, f"●提出代行者氏名：{data_c['提出代行者氏名']}", ln=0)
    pdf.set_xy(right_start_x, y_3+line_height*2)
    pdf.cell(col_width, line_height, f"●届出者との関係：{data_c['届出者との関係']}", ln=0)
    pdf.set_xy(right_start_x, y_3+line_height*3)
    pdf.cell(col_width, line_height, f"●続柄：{data_c['続柄']}", ln=0)
    pdf.set_xy(right_start_x, y_3+line_height*4)
    pdf.cell(col_width, line_height, f"●事業所名：{data_c['事業所名']}", ln=1)
    pdf.ln(5)
    
    right_y = pdf.get_y()


    # ラインを全体に引く
    line_set_y = max(left_y, right_y)
    pdf.line(left_margin, line_set_y, left_margin + page_width, line_set_y)

    pdf.ln(10)

    pdf.cell(0, line_height, "●一時停止・再開の別", ln=1)
    pdf.set_xy(15, pdf.get_y())
    pdf.cell(0, line_height, f"{data_c['一時停止・再開の別']}", ln=1)
    pdf.ln(10)
    pdf.cell(0, line_height, "●一時停止・再開の理由", ln=1)
    pdf.set_xy(15, pdf.get_y())
    pdf.multi_cell(pdf.w - 30, 7, f"{data_c['一時停止・再開の理由']}", ln=1)
    pdf.ln(10)
    pdf.cell(0, line_height, "●一時停止・再開予定日", ln=1)
    pdf.set_xy(15, pdf.get_y())
    pdf.cell(0, line_height, f"{data_c['一時停止・再開予定日']}", ln=1)


    # PDF 保存
    pdf_file = folder_path_c / f"変更届({reception_id}).pdf"
    pdf.output(str(pdf_file))


# ======================================== 中止のページ =========================================

# -----------------------------中止のバリデーション関数-------------------------------
def validate_stop(data_s: dict):
    input_error_s = []
    # ----- 必須入力項目チェック -----
    stop_field = ["住所", "氏名", "中止の理由", "中止予定日"]
    for field in stop_field:
        if not data_s.get(field):
            input_error_s.append(f"{field}")
    # ----- 代行届出チェック -----
    if data_s.get("提出代行者氏名"):
        for field in ["届出者との関係", "事業所名", "続柄"]:
            if not data_s.get(field) or data_s.get(field) == "選択してください":
                input_error_s.append(f"{field}") 
    
    # ----- エラー表示 -----
    if input_error_s:
        st.error(f"{" , ".join(input_error_s)}を入力・選してください")
        return False
    
    return True

# ----------------------------中止の保存処理関数 ----------------------------------------
def save_stop(data_s: dict, reception_id):
    # ----- 保存先ベースフォルダを作る -----
    BASE_DIR_S = Path("3_chuushi")
    BASE_DIR_S.mkdir(exist_ok=True)

    # ----- フォルダ名を　名前_記入年月日　にして作る
    folder_name_s = f"{data_s["氏名"]}_{datetime.date.today().strftime("%Y%m%d")}"
    folder_path_s = BASE_DIR_S / folder_name_s
    folder_path_s.mkdir(exist_ok=True)

    # ----- csv保存 -----
    csv_file_s = folder_path_s / "info.csv"
    headers_s = list(data_s.keys())
    with open(csv_file_s, "w", newline="", encoding="cp932") as f:
        writer_s = csv.DictWriter(f, fieldnames=headers_s)
        writer_s.writeheader()
        writer_s.writerow(data_s)
    
    # ::::::::::::::::::::::::::::::::::::: pdf保存 :::::::::::::::::::::::::::::::::::::
    pdf = FPDF(format="A4")
    pdf.add_page()

    pdf.set_left_margin(15)   # 左余白を 10mm → 15mm に
    pdf.set_right_margin(15)  # 右余白を 10mm → 15mm に
    pdf.set_top_margin(10)    # 上余白は必要に応じて

    # フォント設定
    font_path = Path(__file__).parent / "fonts" / "NotoSansJP-Regular.ttf"
    pdf.add_font("NotoSansJP", "", str(font_path), uni=True)

    # タイトル
    pdf.set_font("NotoSansJP", "", 16)
    pdf.cell(0, 12, "三木市ふれあい収集利用中止届", ln=1, align="C")
    
    # フォントを通常に戻す
    pdf.set_font("NotoSansJP", "", 12)
    pdf.cell(0, 12, f"記入年月日：{data_s['記入年月日']}", ln=1)

    pdf.ln(5)
    y_2 = pdf.get_y()

     # ラインを全体に引く
    left_margin = 15
    right_margin = 15
    page_width = pdf.w - left_margin - right_margin
    pdf.line(left_margin, y_2, left_margin + page_width, y_2)

    pdf.ln(5)
    y_3 = pdf.get_y()

    # ページ幅を考慮した列幅
    col_width = pdf.w / 2 - 15  # 左右列の幅
    line_height = 9  # 行の高さ

    # ===== 左列：申請者情報 =====
    pdf.set_xy(15, y_3)  # 左上の座標
    pdf.cell(col_width, line_height, "----------申請者情報----------", ln=1)
    pdf.cell(col_width, line_height, f"●氏名：{data_s['氏名']}", ln=1)
    pdf.cell(col_width, line_height, "●住所：", ln=1)
    pdf.multi_cell(col_width, line_height, f"{data_s['住所']}", ln=1)
  
    left_y = pdf.get_y()

    # ===== 右列：提出代行者情報 =====
    right_start_x = pdf.w/2 + 5
    pdf.set_xy(right_start_x, y_3)  # 右列開始位置
    pdf.cell(col_width, line_height, "----------代行届出の場合----------", ln=0)
    pdf.set_xy(right_start_x, y_3+line_height)
    pdf.cell(col_width, line_height, f"●提出代行者氏名：{data_s['提出代行者氏名']}", ln=0)
    pdf.set_xy(right_start_x, y_3+line_height*2)
    pdf.cell(col_width, line_height, f"●届出者との関係：{data_s['届出者との関係']}", ln=0)
    pdf.set_xy(right_start_x, y_3+line_height*3)
    pdf.cell(col_width, line_height, f"●続柄：{data_s['続柄']}", ln=0)
    pdf.set_xy(right_start_x, y_3+line_height*4)
    pdf.cell(col_width, line_height, f"●事業所名：{data_s['事業所名']}", ln=1)
    pdf.ln(5)
    
    right_y = pdf.get_y()


    # ラインを全体に引く
    line_set_y = max(left_y, right_y)
    pdf.line(left_margin, line_set_y, left_margin + page_width, line_set_y)

    pdf.ln(10)

    pdf.cell(0, line_height, "●中止の理由", ln=1)
    pdf.set_xy(15, pdf.get_y())
    pdf.cell(0, line_height, f"{data_s['中止の理由']}", ln=1)
    pdf.ln(10)
    pdf.cell(0, line_height, "●中止予定日", ln=1)
    pdf.set_xy(15, pdf.get_y())
    pdf.multi_cell(pdf.w - 30, 7, f"{data_s['中止予定日']}", ln=1)
    
    # PDF 保存
    pdf_file = folder_path_s / f"中止届({reception_id}).pdf"
    pdf.output(str(pdf_file))
