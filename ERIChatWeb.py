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

    elif "基本資料" in query or "公司概況" in query:
        match = re.search(r"一[、.\s]*公司概況\s*(.+?)二[、.\s]*營業項目", text, re.DOTALL)
        return "✅ 能資公司基本資料：\n" + match.group(1).strip() if match else "❌ 找不到公司概況內容。"

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
