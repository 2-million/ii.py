from flask import Flask, request, jsonify, send_file, render_template_string
from ultralytics import YOLO
import cv2
import numpy as np
import os
from datetime import datetime
from ii.database import save_to_db, get_records
from ii.report import create_pdf_report, BASE_DIR

app = Flask(__name__)
model = YOLO('yolov8n.pt')
os.makedirs('static', exist_ok=True)

with open(os.path.join(os.path.dirname(__file__), 'index.html'), 'r', encoding='utf-8') as f:
    HTML_TEMPLATE = f.read()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/process', methods=['POST'])
def process_image():
    file = request.files['image']
    
    img_bytes = file.read()
    img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    
    results = model(img, conf=0.3)
    
    boxes = results[0].boxes
    
    couches = [] 
    animals = [] 
    violations = 0
    
    for box in boxes:
        cls_id = int(box.cls[0])
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        
        if cls_id == 57:
            couches.append((x1, y1, x2, y2))
        
        if cls_id in [15, 16]:
            animal_name = "cat" if cls_id == 15 else "dog"
            animals.append((x1, y1, x2, y2, animal_name))
    
    for animal in animals:
        ax1, ay1, ax2, ay2, name = animal
        center_x = (ax1 + ax2) / 2
        center_y = (ay1 + ay2) / 2
        
        for couch in couches:
            cx1, cy1, cx2, cy2 = couch
            if cx1 < center_x < cx2 and cy1 < center_y < cy2:
                violations += 1
                
                cv2.rectangle(img, (int(ax1), int(ay1)), (int(ax2), int(ay2)), (0, 0, 255), 3)
                cv2.putText(img, f"VIOLATION! {name}", (int(ax1), int(ay1) - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    
    output_img = results[0].plot()
    output_img = cv2.addWeighted(output_img, 0.7, img, 0.3, 0)
    
    output_path = 'static/result.jpg'
    cv2.imwrite(output_path, output_img)
    
    cats = sum(1 for b in boxes if int(b.cls[0]) == 15)
    dogs = sum(1 for b in boxes if int(b.cls[0]) == 16)
    couches_count = sum(1 for b in boxes if int(b.cls[0]) == 57)
    total_objects = len(boxes)
    
    save_to_db(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_objects=total_objects,
        cats=cats,
        dogs=dogs,
        couches=couches_count,
        violations=violations
    )
    
    return jsonify({
        'count': total_objects,
        'cats': cats,
        'dogs': dogs,
        'couches': couches_count,
        'violations': violations,
        'has_violation': violations > 0
    })

@app.route('/export/pdf')
def export_pdf():
    records = get_records()
    create_pdf_report(records)
    return send_file(os.path.join(BASE_DIR, 'report.pdf'), as_attachment=True)