"""
Генерация PDF отчета для пациента
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime

# Попытка зарегистрировать русский шрифт (если есть)
try:
    # Для Windows
    font_path = "C:/Windows/Fonts/arial.ttf"
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Arial', font_path))
        RUSSIAN_FONT = 'Arial'
    else:
        RUSSIAN_FONT = 'Helvetica'
except:
    RUSSIAN_FONT = 'Helvetica'


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

    # Создаем стили для русского текста
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
    story.append(Paragraph("🦷 Стоматологический помощник", title_style))
    story.append(Paragraph("Результаты прогноза", title_style))
    story.append(Spacer(1, 5 * mm))

    # Дата
    story.append(Paragraph(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}", normal_style))
    story.append(Spacer(1, 3 * mm))

    # Информация о пациенте
    story.append(Paragraph("📋 Информация о пациенте", heading_style))

    patient_info = [
        [f"Имя: {patient_name if patient_name else 'Не указано'}"],
        [f"Возраст: {patient_data.get('возраст', 'Не указан')} лет"],
        [f"Пол: {patient_data.get('пол', 'Не указан')}"],
    ]

    patient_table = Table(patient_info, colWidths=[80 * mm])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), RUSSIAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 5 * mm))

    # Результаты прогноза
    story.append(Paragraph("📊 Результаты прогноза", heading_style))

    # КПУ
    kpu = results.get('КПУ', 0)
    if kpu < 3:
        kpu_status = "Низкий риск кариеса"
        kpu_color = "🟢"
    elif kpu < 7:
        kpu_status = "Средний риск кариеса"
        kpu_color = "🟡"
    else:
        kpu_status = "Высокий риск кариеса"
        kpu_color = "🔴"

    results_data = [
        [f"🦷 КПУ (индекс кариеса)", f"{kpu:.1f} - {kpu_status}"],
    ]

    # Пародонтит
    paro = results.get('пародонтит', {})
    if paro.get('risk', False):
        paro_status = f"🔴 Есть риск ({paro.get('risk_percent', 0):.0f}%)"
    else:
        paro_status = f"🟢 Нет риска ({100 - paro.get('risk_percent', 0):.0f}%)"
    results_data.append(["🦷 Пародонтит", paro_status])

    # Рефлюкс
    reflux = results.get('рефлюкс', {})
    if reflux.get('risk', False):
        reflux_status = f"🔴 Есть риск ({reflux.get('risk_percent', 0):.0f}%)"
    else:
        reflux_status = f"🟢 Нет риска ({100 - reflux.get('risk_percent', 0):.0f}%)"
    results_data.append(["🔥 Рефлюкс", reflux_status])

    # Фтор в моче
    fluorine = results.get('фтор_моча_кг', 0)
    if fluorine < 0.3:
        fluorine_status = f"🟡 {fluorine:.2f} мкг/кг (низкий)"
    elif fluorine < 1.5:
        fluorine_status = f"🟢 {fluorine:.2f} мкг/кг (оптимальный)"
    else:
        fluorine_status = f"🔴 {fluorine:.2f} мкг/кг (высокий)"
    results_data.append(["💧 Фтор в моче", fluorine_status])

    results_table = Table(results_data, colWidths=[60 * mm, 80 * mm])
    results_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), RUSSIAN_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
    ]))
    story.append(results_table)
    story.append(Spacer(1, 5 * mm))

    # Рекомендации
    story.append(Paragraph("💡 Клинические рекомендации", heading_style))

    from utils.recommendations import generate_recommendations
    recommendations = generate_recommendations(results)

    if recommendations:
        for rec in recommendations:
            story.append(Paragraph(f"• {rec['text']}", normal_style))
    else:
        story.append(
            Paragraph("• Значимых отклонений не выявлено. Поддерживайте обычную гигиену полости рта.", normal_style))

    story.append(Spacer(1, 10 * mm))

    # Подвал
    story.append(Paragraph("---", normal_style))
    story.append(Paragraph("ℹ️ Данный отчет сгенерирован автоматически на основе ML моделей.",
                           ParagraphStyle('Footer', parent=normal_style, fontSize=8,
                                          textColor=colors.HexColor('#95a5a6'))))
    story.append(Paragraph("Прогноз носит рекомендательный характер. Окончательное решение принимает врач.",
                           ParagraphStyle('Footer2', parent=normal_style, fontSize=8,
                                          textColor=colors.HexColor('#95a5a6'))))

    # Создаем PDF
    doc.build(story)

    return filename