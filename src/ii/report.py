import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
pdfmetrics.registerFont(TTFont('Arial', '/System/Library/Fonts/Supplemental/Arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold', '/System/Library/Fonts/Supplemental/Arial Bold.ttf'))
FONT = 'Arial'
FONT_BOLD = 'Arial-Bold'

def create_pdf_report(records):
    path = os.path.join(BASE_DIR, 'report.pdf')
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    
    # заголовок
    c.setFont(FONT_BOLD, 16)
    c.drawString(50, height - 50, "Отчет: Контроль доступа животных")
    
    # статистика
    c.setFont(FONT, 11)
    y = height - 90
    total_checks = len(records)
    total_violations = sum(r[6] for r in records)
    c.drawString(50, y, f"Всего проверок: {total_checks}")
    c.drawString(50, y - 20, f"Всего нарушений: {total_violations}")
    
    # таблица
    y -= 60
    c.setFont(FONT_BOLD, 12)
    c.drawString(50, y, "История проверок:")
    c.setFont(FONT, 9)
    y -= 25
    
    for row in records:
        if y < 50:
            c.showPage()
            y = height - 50
        
        c.drawString(50, y, f"ID: {row[0]} | Время: {row[1]}")
        c.drawString(50, y - 12, f"Объектов: {row[2]} | Кошек: {row[3]} | Собак: {row[4]} | Диванов: {row[5]}")
        
        if row[6] > 0:
            c.setFillColorRGB(1, 0, 0)
            c.drawString(50, y - 24, f"НАРУШЕНИЙ: {row[6]}")
            c.setFillColorRGB(0, 0, 0)
        else:
            c.drawString(50, y - 24, "Нарушений нет")
        
        y -= 45
    
    c.save()