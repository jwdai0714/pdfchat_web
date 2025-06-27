# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
from pypdf import PdfReader
import re

app = Flask(__name__)

# 載入 PDF 並轉成文字
def load_pdf_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

pdf_text = load_pdf_text("EnergyResource.pdf")

# 問答邏輯
def answer_question(text, query):
    query = query.strip().lower()

    if "英文" in query and "公司" in query:
        match = re.search(r"能資國際股份有限公司（([A-Za-z ,\.]+)）", text)
        return f"公司英文名稱：{match.group(1)}" if match else "❌ 找不到公司英文名稱。"

    elif "成立" in query or "創立" in query:
        match = re.search(r"成立時間[:：\s]?([0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日)", text)
        return f"成立時間：{match.group(1)}" if match else "❌ 找不到成立時間。"

    elif "資本" in query:
        match = re.search(r"實收資本額[:：\s]?([^\n]+)", text)
        return f"實收資本額：{match.group(1)}" if match else "❌ 找不到資本資訊。"

    elif "董事長" in query or "負責人" in query:
        match = re.search(r"(負責人|董事長)[:：\s]?([^\n]+)", text)
        return f"{match.group(1)}：{match.group(2)}" if match else "❌ 找不到負責人資訊。"

    elif "員工" in query or "人數" in query:
        match = re.search(r"員工人數[:：]?\s*約?\s*([^\n]+)", text)
        return f"✅ 員工人數：約 {match.group(1)}" if match else "❌ 找不到員工人數資訊。"

    elif "地址" in query or "地點" in query:
        match = re.search(r"地址[:：]?\s*([^\n]+)", text)
        return f"✅ 公司地址：{match.group(1)}" if match else "❌ 找不到地址資訊。"

    elif "基本資料" in query or "公司概況" in query:
        match = re.search(r"一[、.\s]*公司概況\s*(.+?)二[、.\s]*營業項目", text, re.DOTALL)
        return "✅ 能資公司基本資料：\n" + match.group(1).strip() if match else "❌ 找不到公司概況內容。"

    elif "認證" in query:
        # 抓取帶有年份 + 認證字樣 的完整句子
        matches = re.findall(r"(20[0-9]{2}年[^\n。]*(?:TFDA|FDA|ISO\s?13485|GMP|QMS)[^\n。]*[。])", text)
        matches = list(dict.fromkeys(matches))  # 去重複
        return "✅ 認證紀錄：\n" + "\n".join(matches) if matches else "❌ 無法找到認證紀錄。"

    elif "產品" in query and ("特色" in query or "規格" in query):
        match = re.search(r"五、產品規格與特徵(.+?)六、應用場景", text, re.DOTALL)
        return "✅ 產品規格與特徵：\n" + match.group(1).strip() if match else "❌ 找不到產品規格與特徵。"

    elif "應用" in query and ("場景" in query or "環境" in query):
        match = re.search(r"六、應用場景與實證案例(.+?)七、AI智慧醫療", text, re.DOTALL)
        return "✅ 應用場景與環境：\n" + match.group(1).strip() if match else "❌ 找不到應用場景內容。"

    elif "環境" in query or "待遇" in query:
        return """✅ 能資公司工作環境與待遇資訊（非公開文件資料，以下為推估）：\n• 員工人數少，扁平化組織，溝通效率高\n• 位於新竹生醫園區，工作環境乾淨明亮\n• 以技術研發為主軸，研發人員為核心團隊\n• 依職務不同，月薪約落在35,000~70,000元不等\n• 員工具備跨領域整合能力，研發自由度高\n• 福利方面提供勞健保、特休、專案獎金與彈性工時\n※ 若需進一步精確薪資與職缺資訊，建議查詢 104 職缺或聯繫人資部門。"""

    elif "軟體" in query or "AI" in query:
        match = re.search(r"七、AI智慧醫療整合系統(.+?)八、技術貢獻", text, re.DOTALL)
        return "✅ 軟體系統：\n" + match.group(1).strip() if match else "❌ 無法找到軟體資訊。"

    elif "技術貢獻" in query or "產業貢獻" in query:
        match = re.search(r"八[、.\s]*技術貢獻與產業價值\s*([\s\S]*)九、獲獎", text)
        return "✅ 能資公司技術貢獻與產業價值：\n" + match.group(1).strip() if match else "❌ 無法找到技術貢獻內容。"

    elif "技術" in query or "核心技術" in query or "技術亮點" in query:
        match = re.search(r"四、核心技術亮點\s*(.*?)五、產品規格與特徵", text, re.S)
        return "✅ 能資公司核心技術亮點：\n" + match.group(1).strip() if match else "❌ 無法找到核心技術亮點內容。"

    elif "產品" in query:
        match = re.search(r"五、產品規格與特徵(.+?)六、應用場景", text, re.DOTALL)
        return "✅ 產品規格與特徵：\n" + match.group(1).strip() if match else "❌ 找不到產品規格與特徵。"

    elif "經營理念" in query or "宗旨" in query or "目標" in query:
        return """✅ 能資公司經營理念（推估自公司概況）：\n以奈米碳管 X 光技術為核心，結合 AI 與遠距診療、在宅醫療應用，致力於改善醫療可近性、提升偏鄉與緊急醫療效率，並建立台灣自主醫療設備研發供應鏈。"""

    elif "獎" in query or "得獎" in query or "獲獎" in query:
        match = re.search(r"九[、.\s]*獲獎\s*(.+)", text, re.DOTALL)
        return "✅ 能資公司獲獎紀錄：\n" + match.group(1).strip() if match else "❌ 找不到獲獎紀錄內容。"

    else:
        return "❓ 此問題無法處理，請明確描述問題內容。"


# 首頁
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# 查詢處理
@app.route("/ask", methods=["POST"])
def ask():
    query = request.form["query"]
    answer = answer_question(pdf_text, query)
    return render_template("index.html", question=query, answer=answer)

if __name__ == "__main__":
    app.run(debug=True)
