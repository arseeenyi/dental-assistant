"""
Генерация PDF отчета для пациента (ИСПРАВЛЕННАЯ ВЕРСИЯ)
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime


# Регистрация русских шрифтов
def register_russian_fonts():
    """Регистрация шрифтов с поддержкой кириллицы"""
    # Пути к шрифтам Windows
    font_paths = [
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/ariali.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/times.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
    ]

    for path in font_paths:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont('RussianFont', path))
                return 'RussianFont'
            except:
                continue

    # Если русский шрифт не найден, используем стандартный
    return 'Helvetica'


RUSSIAN_FONT = register_russian_fonts()


def generate_pdf_report(results, patient_data, patient_name, filename="dental_report.pdf"):
    """
    Генерация PDF отчета

    Args:
        results: словарь с результатами прогноза
        patient_data: словарь с данными пациента
        patient_name: имя пациента
        filename: имя файла для сохранения

    Returns:
        str: путь к созданному файлу
    """

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm
    )

    styles = getSampleStyleSheet()

    # Создаем стили с поддержкой русского языка
    title_style = ParagraphStyle(
        'RussianTitle',
        parent=styles['Title'],
        fontName=RUSSIAN_FONT,
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        alignment=1,  # Центр
        spaceAfter=10
    )

    heading_style = ParagraphStyle(
        'RussianHeading',
        parent=styles['Heading2'],
        fontName=RUSSIAN_FONT,
        fontSize=12,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=12
    )

    normal_style = ParagraphStyle(
        'RussianNormal',
        parent=styles['Normal'],
        fontName=RUSSIAN_FONT,
        fontSize=10,
        spaceAfter=6
    )

    # Собираем контент
    story = []

    # Заголовок
    story.append(Paragraph("Stomatologic Assistant", title_style))
    story.append(Paragraph("Dental Health Prediction Report", title_style))
    story.append(Spacer(1, 5 * mm))

    # Дата на русском
    date_str = datetime.now().strftime("%d.%m.%Y %H:%M")
    story.append(Paragraph(f"Date: {date_str}", normal_style))
    story.append(Spacer(1, 3 * mm))

    # Информация о пациенте
    story.append(Paragraph("Patient Information", heading_style))

    # Определяем пол на русском
    gender_text = "Male" if patient_data.get('gender') == "Мужской" else "Female"
    if patient_data.get('пол') == 1:
        gender_text = "Male"
    elif patient_data.get('пол') == 0:
        gender_text = "Female"

    patient_info = [
        [f"Name:", f"{patient_name if patient_name else 'Not specified'}"],
        [f"Age:", f"{patient_data.get('возраст', 'Not specified')} years"],
        [f"Gender:", f"{gender_text}"],
    ]

    patient_table = Table(patient_info, colWidths=[50 * mm, 90 * mm])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), RUSSIAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#ecf0f1')),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 5 * mm))

    # Результаты прогноза
    story.append(Paragraph("Prediction Results", heading_style))

    # КПУ
    kpu = results.get('КПУ', 0)
    if kpu < 3:
        kpu_status = "Low caries risk"
        kpu_color = '#27ae60'
    elif kpu < 7:
        kpu_status = "Medium caries risk"
        kpu_color = '#f39c12'
    else:
        kpu_status = "High caries risk"
        kpu_color = '#e74c3c'

    # Пародонтит
    paro = results.get('пародонтит', {})
    if paro.get('risk', False):
        paro_status = f"Risk detected ({paro.get('risk_percent', 0):.0f}%)"
        paro_color = '#e74c3c'
    else:
        paro_status = f"No risk ({100 - paro.get('risk_percent', 0):.0f}%)"
        paro_color = '#27ae60'

    # Рефлюкс
    reflux = results.get('рефлюкс', {})
    if reflux.get('risk', False):
        reflux_status = f"Risk detected ({reflux.get('risk_percent', 0):.0f}%)"
        reflux_color = '#e74c3c'
    else:
        reflux_status = f"No risk ({100 - reflux.get('risk_percent', 0):.0f}%)"
        reflux_color = '#27ae60'

    # Фтор в моче
    fluorine = results.get('фтор_моча_кг', 0)
    if fluorine < 0.3:
        fluorine_status = f"{fluorine:.2f} mcg/kg (Low)"
        fluorine_color = '#f39c12'
    elif fluorine < 1.5:
        fluorine_status = f"{fluorine:.2f} mcg/kg (Optimal)"
        fluorine_color = '#27ae60'
    else:
        fluorine_status = f"{fluorine:.2f} mcg/kg (High)"
        fluorine_color = '#e74c3c'

    results_data = [
        ["Indicator", "Value", "Status"],
        ["Dental Caries (DMFT)", f"{kpu:.1f}", kpu_status],
        ["Periodontitis", "-", paro_status],
        ["Reflux", "-", reflux_status],
        ["Urine Fluorine", fluorine_status, ""],
    ]

    results_table = Table(results_data, colWidths=[50 * mm, 45 * mm, 55 * mm])
    results_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), RUSSIAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 0), (2, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (2, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(results_table)
    story.append(Spacer(1, 5 * mm))

    # Рекомендации
    story.append(Paragraph("Clinical Recommendations", heading_style))

    from utils.recommendations import generate_recommendations
    recommendations = generate_recommendations(results)

    if recommendations:
        for rec in recommendations:
            # Переводим рекомендации на английский для отчета
            text = rec['text']
            # Заменяем русские фразы на английские (упрощенно)
            text = text.replace("Высокий индекс КПУ", "High DMFT index")
            text = text.replace("Средний индекс КПУ", "Medium DMFT index")
            text = text.replace("Низкий индекс КПУ", "Low DMFT index")
            text = text.replace("Рекомендуется", "Recommended")
            text = text.replace("риск пародонтита", "periodontitis risk")
            text = text.replace("риск рефлюкса", "reflux risk")
            text = text.replace("Низкий уровень фтора", "Low fluorine level")
            text = text.replace("Повышенный уровень фтора", "High fluorine level")
            story.append(Paragraph(f"• {text}", normal_style))
    else:
        story.append(Paragraph("• No significant abnormalities detected. Maintain regular oral hygiene.", normal_style))

    story.append(Spacer(1, 10 * mm))

    # Подвал
    story.append(Paragraph("---", normal_style))
    story.append(Paragraph("This report was generated automatically using ML models trained on clinical data.",
                           ParagraphStyle('Footer', parent=normal_style, fontSize=8,
                                          textColor=colors.HexColor('#95a5a6'))))
    story.append(Paragraph("The prediction is for reference only. The final decision should be made by a physician.",
                           ParagraphStyle('Footer2', parent=normal_style, fontSize=8,
                                          textColor=colors.HexColor('#95a5a6'))))

    # Создаем PDF
    doc.build(story)

    return filename