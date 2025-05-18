# app.py
from flask import Flask, request, jsonify, render_template
from trie import Trie
import pdfplumber
import re
import io

app = Flask(__name__, template_folder='templates')

trie = Trie()
pdf_index = {}
last_uploaded_pdf_stream = None

# Initial sample words
words_with_frequencies = [
    ("apple", 8), ("angle", 7), ("ant", 9),
    ("banana", 6), ("boat", 7), ("breeze", 5),
    ("cat", 10), ("candle", 8), ("cave", 6),
]
base_words = ["hello", "hero", "heat", "heap", "helmet", "help", "happy", "hope"]

for word in base_words:
    trie.insert(word, 10)
for word, freq in words_with_frequencies:
    trie.insert(word, freq)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/autocomplete")
def autocomplete():
    prefix = request.args.get("prefix", "").lower()
    suggestions = trie.auto_suggest(prefix)
    return jsonify(suggestions)

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    global pdf_index, last_uploaded_pdf_stream
    file = request.files["file"]
    if file and file.filename.endswith(".pdf"):
        pdf_index.clear()
        last_uploaded_pdf_stream = io.BytesIO(file.read())
        last_uploaded_pdf_stream.seek(0)

        with pdfplumber.open(last_uploaded_pdf_stream) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text:
                    continue
                words = re.findall(r'\b\w+\b', text.lower())
                for word in words:
                    trie.insert(word, 1)
                    if word not in pdf_index:
                        pdf_index[word] = set()
                    pdf_index[word].add(i + 1)

        return "PDF content indexed successfully!"
    return "Invalid file format", 400

@app.route("/word_info")
def word_info():
    word = request.args.get("word", "").lower()
    if word in pdf_index:
        return jsonify([{"page": p} for p in sorted(pdf_index[word])])
    else:
        return jsonify([])

@app.route("/page_texts")
def page_texts():
    word = request.args.get("word", "").lower()
    if word not in pdf_index or not last_uploaded_pdf_stream:
        return jsonify([])

    page_results = []
    last_uploaded_pdf_stream.seek(0)
    with pdfplumber.open(last_uploaded_pdf_stream) as pdf:
        for p in sorted(pdf_index[word]):
            page = pdf.pages[p - 1]
            text = page.extract_text()
            page_results.append({
                "page": p,
                "text": text.strip() if text else "[No text on page]"
            })

    return jsonify(page_results)

if __name__ == "__main__":
    app.run(debug=True)
