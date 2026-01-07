import os
import io
import whisper
import fitz  # PyMuPDF
from flask import Flask, render_template, request, send_file, jsonify
from pathlib import Path
import tempfile

app = Flask(__name__)
BASE_DIR = Path(__file__).parent
TEMPLATE_PDF = BASE_DIR / "assets" / "RCC_Wilms_Tumor_Template.pdf"

# โหลดโมเดล (ใช้ base เพื่อประหยัด RAM บน Cloud)
model = whisper.load_model("base")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/auto-generate", methods=["POST"])
def auto_generate():
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "No file uploaded"}), 400

    try:
        # 1. ประมวลผลเสียงผ่าน Temporary File (จะถูกลบทันทีที่ใช้เสร็จ)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio_file.save(tmp.name)
            tmp_path = tmp.name
        
        result = model.transcribe(tmp_path)
        text = result["text"].lower()
        os.remove(tmp_path) # ลบไฟล์เสียงทิ้งทันที

        # 2. Logic สกัดข้อมูล (ตัวอย่าง)
        mock_side = "right" if "right" in text else "left"
        
        # 3. สร้าง PDF ใน Memory (BytesIO)
        doc = fitz.open(TEMPLATE_PDF)
        page = doc[0]
        
        # ค้นหาและวงกลม (Logic ของคุณ)
        insts = page.search_for(mock_side)
        for inst in insts:
            page.draw_oval(inst + (-2, -2, 2, 2), color=(1, 0, 0), width=1.5)

        # บันทึกลงแรม
        pdf_stream = io.BytesIO()
        doc.save(pdf_stream)
        doc.close()
        pdf_stream.seek(0)

        return send_file(
            pdf_stream,
            mimetype='application/pdf',
            download_name="report.pdf"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)