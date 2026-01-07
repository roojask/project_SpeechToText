import os
import io
import time
import fitz  # PyMuPDF
from flask import Flask, render_template, request, send_file, jsonify
from pathlib import Path

app = Flask(__name__)

# --- Config สำหรับ Replit ---
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
# ไฟล์ต้นฉบับที่คุณอัปโหลดไว้
TEMPLATE_PDF = ASSETS_DIR / "RCC_Wilms_Tumor_Template.pdf"

# ตรวจสอบว่ามีโฟลเดอร์ assets หรือยัง
if not ASSETS_DIR.exists():
    ASSETS_DIR.mkdir(exist_ok=True)

def circle_text(page, text_to_circle):
    """ ค้นหาคำใน PDF และวาดวงกลมสีแดง """
    if not text_to_circle: return
    text_instances = page.search_for(text_to_circle)
    for inst in text_instances:
        # วาดวงกลมรอบตำแหน่งที่เจอ
        rect = fitz.Rect(inst.x0 - 2, inst.y0 - 2, inst.x1 + 2, inst.y1 + 2)
        shape = page.new_shape()
        shape.draw_oval(rect)
        shape.finish(color=(1, 0, 0), width=1.5)
        shape.commit()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/auto-generate", methods=["POST"])
def auto_generate():
    # รับไฟล์เสียงจากหน้าเว็บ
    audio_file = request.files.get("audio")
    if not audio_file:
        return jsonify({"error": "No audio file received"}), 400

    try:
        # --- ขั้นตอนจำลอง AI (Mock AI Logic) ---
        # เพื่อหลีกเลี่ยง Memory Limit บน Replit
        time.sleep(2) # จำลองว่า AI กำลังคิด
        
        # สมมติผลลัพธ์ที่ AI วิเคราะห์ได้จากเสียงของคุณ
        mock_side = "right" # สมมติว่าได้ยินคำว่า right
        mock_dims = "5.5 x 4.2 x 3.0" # สมมติขนาดที่แกะได้

        # --- จัดการ PDF ในหน่วยความจำ (In-memory) ---
        if not TEMPLATE_PDF.exists():
            return jsonify({"error": "Template PDF missing in assets/"}), 500
            
        doc = fitz.open(str(TEMPLATE_PDF))
        page = doc[0]

        # วงกลมข้าง (Right/Left)
        circle_text(page, mock_side)

        # เขียนขนาดตัวเลขสีแดงลงใน PDF (หลังคำว่า Measuring)
        hits = page.search_for("Measuring")
        if hits:
            # วางข้อความที่ตำแหน่งพิกัด x, y
            page.insert_text((hits[0].x1 + 10, hits[0].y1), mock_dims, color=(1,0,0), fontsize=11)

        # บันทึกไฟล์ลงใน RAM (BytesIO) ไม่เขียนลง Disk เพื่อไม่ให้ Checkpoint พัง
        pdf_stream = io.BytesIO()
        doc.save(pdf_stream)
        doc.close()
        pdf_stream.seek(0)

        # ส่งไฟล์ PDF กลับไปให้ผู้ใช้ดาวน์โหลดหรือพรีวิวทันที
        return send_file(
            pdf_stream,
            mimetype='application/pdf',
            download_name="Pathology_Report.pdf",
            as_attachment=False
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Replit ต้องใช้พอร์ต 8080
    app.run(host='0.0.0.0', port=8080, debug=True)