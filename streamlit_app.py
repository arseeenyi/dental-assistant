"""
СТОМАТОЛОГИЧЕСКИЙ ПОМОЩНИК
Веб-приложение для прогнозирования стоматологических показателей
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Добавляем текущую директорию в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from model_inference import DentalPredictor
from utils.validators import validate_age, validate_height, validate_weight, validate_ph, validate_fluorine
from utils.formatters import format_kpu, format_risk, format_fluorine, get_kpu_color, get_fluorine_color
from utils.recommendations import generate_recommendations
from utils.history_manager import load_history, save_history, add_prediction, clear_history, export_history_to_csv
from utils.pdf_generator import generate_pdf_report

# ============================================
# НАСТРОЙКА СТРАНИЦЫ
# ============================================

st.set_page_config(
    page_title="Стоматологический помощник",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Кастомные стили
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 0.25rem;
    }
    .sub-header {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        height: 100%;
        min-height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.2rem 0;
    }
    .risk-high {
        color: #e74c3c;
        font-weight: bold;
    }
    .risk-low {
        color: #27ae60;
        font-weight: bold;
    }
    .recommendation-box {
        background-color: #e8f4fd;
        border-left: 4px solid #3498db;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-radius: 8px;
    }
    .results-header {
        font-size: 1.3rem;
        font-weight: bold;
        margin: 1rem 0 0.5rem 0;
        color: #2c3e50;
    }
    .divider {
        margin: 1rem 0;
        border-top: 1px solid #e0e0e0;
    }
    .confidence-low {
        color: #e74c3c;
        font-size: 0.8rem;
    }
    .confidence-medium {
        color: #f39c12;
        font-size: 0.8rem;
    }
    .confidence-high {
        color: #27ae60;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# ЗАГРУЗКА МОДЕЛЕЙ
# ============================================

@st.cache_resource
def load_predictor():
    try:
        with st.spinner("🔄 Загрузка моделей..."):
            predictor = DentalPredictor()
        return predictor
    except Exception as e:
        st.error(f"❌ Ошибка загрузки моделей: {e}")
        return None


predictor = load_predictor()

if predictor is None:
    st.stop()

# ============================================
# ИНИЦИАЛИЗАЦИЯ SESSION_STATE
# ============================================

if 'history' not in st.session_state:
    st.session_state.history = load_history()  # ЗАГРУЖАЕМ ИЗ ФАЙЛА
if 'current_results' not in st.session_state:
    st.session_state.current_results = None
if 'patient_name' not in st.session_state:
    st.session_state.patient_name = ""

# ============================================
# ЗАГОЛОВОК
# ============================================

st.markdown('<div class="main-header">🦷 Стоматологический помощник</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Прогнозирование КПУ, пародонтита, рефлюкса и уровня фтора</div>',
            unsafe_allow_html=True)

# ============================================
# ВЕРХНЯЯ ЧАСТЬ - ФОРМА ВВОДА ДАННЫХ
# ============================================

with st.container():
    st.markdown("### 📝 Данные пациента")

    # Имя пациента
    patient_name = st.text_input(
        "👤 Имя пациента (опционально)",
        value=st.session_state.patient_name,
        placeholder="Например: Иванов И.И.",
        key="patient_name_input"
    )
    st.session_state.patient_name = patient_name

    # Вкладки для ввода
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Личные данные", "🧪 Лабораторные", "💧 Фтор", "⚕️ Факторы риска"])

    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input("📅 Возраст (лет)", min_value=0, max_value=120, value=35, step=1)
        with col2:
            height = st.number_input("📏 Рост (см)", min_value=50, max_value=250, value=170, step=1)
        with col3:
            weight = st.number_input("⚖️ Вес (кг)", min_value=10, max_value=300, value=70, step=1)

        gender = st.radio("🚻 Пол", ["Мужской", "Женский"], horizontal=True)
        gender_value = 1 if gender == "Мужской" else 0

    with tab2:
        col1, col2, col3 = st.columns(3)
        with col1:
            ph_saliva = st.slider("💧 pH слюны", 5.0, 8.5, 6.8, 0.05, help="Норма: 6.5-7.5")
        with col2:
            ph_water = st.slider("🚰 pH воды", 6.0, 8.5, 7.0, 0.05, help="Норма: 6.5-8.5")
        with col3:
            ph_tea = st.slider("🍵 pH чая", 5.0, 8.0, 6.5, 0.05, help="Норма: 5.5-7.0")

    with tab3:
        col1, col2, col3 = st.columns(3)
        with col1:
            fluorine_water = st.number_input("💧 Фтор в воде (мг/л)", min_value=0.0, max_value=5.0, value=0.5, step=0.1)
        with col2:
            fluorine_products = st.number_input("🥗 Фтор в продуктах (мг)", min_value=0.0, max_value=100.0, value=10.0,
                                                step=1.0)
        with col3:
            fluorine_tea = st.number_input("🍵 Фтор в чае (мг)", min_value=0.0, max_value=10.0, value=0.5, step=0.1)

    with tab4:
        col1, col2, col3 = st.columns(3)
        with col1:
            smoking = st.radio("🚬 Курение/алкоголь", ["Нет", "Да"], horizontal=True)
            smoking_value = 1 if smoking == "Да" else 0
        with col2:
            bruxism = st.radio("😬 Бруксизм", ["Нет", "Да"], horizontal=True)
            bruxism_value = 1 if bruxism == "Да" else 0
        with col3:
            endocrine = st.radio("🦋 Эндокринные нарушения", ["Нет", "Да"], horizontal=True)
            endocrine_value = 1 if endocrine == "Да" else 0

    # Кнопка прогноза
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("🔮 ПОЛУЧИТЬ ПРОГНОЗ", type="primary", use_container_width=True):
            with st.spinner("🔄 Анализируем данные..."):
                # Формируем данные пациента
                patient_data = {
                    'возраст': age,
                    'рост': height,
                    'вес': weight,
                    'пол': gender_value,
                    'pH_слюны': ph_saliva,
                    'pH_вода': ph_water,
                    'pH_чай': ph_tea,
                    'фтор_вода': fluorine_water,
                    'фтор_продукты': fluorine_products,
                    'фтор_чай': fluorine_tea,
                    'курение_алкоголь': smoking_value,
                    'бруксизм': bruxism_value,
                    'эндокринные': endocrine_value,
                }

                # Получаем признаки из модели
                first_model = list(predictor.models.values())[0]
                required_features = first_model['feature_names']

                for feature in required_features:
                    if feature not in patient_data:
                        patient_data[feature] = np.nan

                try:
                    results = predictor.predict_all(patient_data)
                    st.session_state.current_results = results

                    # Сохраняем в историю
                    history_entry = {
                        'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'patient_name': patient_name if patient_name else "Без имени",
                        'age': age,
                        'gender': gender,
                        'kpu': results['КПУ'],
                        'parodontit_risk': results['пародонтит']['risk'],
                        'parodontit_percent': results['пародонтит']['risk_percent'],
                        'reflux_risk': results['рефлюкс']['risk'],
                        'reflux_percent': results['рефлюкс']['risk_percent'],
                        'fluorine': results['фтор_моча_кг']
                    }
                    # Добавляем в историю с сохранением в файл
                    st.session_state.history = add_prediction(st.session_state.history, history_entry)

                    st.success("✅ Прогноз выполнен успешно!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Ошибка при прогнозе: {e}")

# ============================================
# НИЖНЯЯ ЧАСТЬ - РЕЗУЛЬТАТЫ
# ============================================

if st.session_state.current_results:
    results = st.session_state.current_results

    st.markdown('<div class="results-header">📊 Результаты прогноза</div>', unsafe_allow_html=True)

    # Три карточки в ряд (одинаковой высоты)
    col1, col2, col3 = st.columns(3)

    with col1:
        kpu = results['КПУ']
        kpu_color = get_kpu_color(kpu)

        st.markdown(f"""
                <div class="metric-card">
                    <h3 style="margin: 0;">🦷 КПУ</h3>
                    <div class="metric-value" style="color: {kpu_color}">{kpu:.1f}</div>
                    <p style="margin: 0;"><strong>{format_kpu(kpu)}</strong></p>
                    <div style="height: 1.2rem;"></div>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        paro = results['пародонтит']
        risk_class = "risk-high" if paro['risk'] else "risk-low"
        risk_text = "Есть риск" if paro['risk'] else "Нет риска"

        # Определяем уровень уверенности для отображения
        confidence = paro['risk_percent'] if paro['risk'] else 100 - paro['risk_percent']
        if confidence > 85:
            conf_class = "confidence-high"
            conf_text = "высокая уверенность"
        elif confidence > 65:
            conf_class = "confidence-medium"
            conf_text = "средняя уверенность"
        else:
            conf_class = "confidence-low"
            conf_text = "низкая уверенность"

        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0;">🦷 Пародонтит</h3>
            <div class="metric-value {risk_class}">{risk_text}</div>
            <p style="margin: 0;">Уверенность модели: {confidence:.0f}%</p>
            <p class="{conf_class}" style="margin: 0;">({conf_text})</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        reflux = results['рефлюкс']
        risk_class = "risk-high" if reflux['risk'] else "risk-low"
        risk_text = "Есть риск" if reflux['risk'] else "Нет риска"

        confidence = reflux['risk_percent'] if reflux['risk'] else 100 - reflux['risk_percent']
        if confidence > 85:
            conf_class = "confidence-high"
            conf_text = "высокая уверенность"
        elif confidence > 65:
            conf_class = "confidence-medium"
            conf_text = "средняя уверенность"
        else:
            conf_class = "confidence-low"
            conf_text = "низкая уверенность"

        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0;">🔥 Рефлюкс</h3>
            <div class="metric-value {risk_class}">{risk_text}</div>
            <p style="margin: 0;">Уверенность модели: {confidence:.0f}%</p>
            <p class="{conf_class}" style="margin: 0;">({conf_text})</p>
        </div>
        """, unsafe_allow_html=True)

    # Фтор в моче (отдельная карточка во всю ширину)
    fluorine = results['фтор_моча_кг']
    fluorine_color = get_fluorine_color(fluorine)
    st.markdown(f"""
    <div class="metric-card" style="margin-top: 1rem;">
        <h3 style="margin: 0;">💧 Фтор в моче</h3>
        <div class="metric-value" style="color: {fluorine_color}">{fluorine:.2f} мкг/кг</div>
        <p style="margin: 0;">{format_fluorine(fluorine)}</p>
    </div>
    """, unsafe_allow_html=True)

    # Рекомендации
    st.markdown('<div class="results-header">💡 Клинические рекомендации</div>', unsafe_allow_html=True)

    recommendations = generate_recommendations(results)
    if recommendations:
        for rec in recommendations:
            st.markdown(f'<div class="recommendation-box">📌 {rec["text"]}</div>', unsafe_allow_html=True)
    else:
        st.info("✅ Значимых отклонений не выявлено. Поддерживайте обычную гигиену полости рта.")

    # Кнопка PDF отчета
    col_pdf1, col_pdf2, col_pdf3 = st.columns([1, 2, 1])
    with col_pdf2:
        # Собираем данные пациента для PDF
        patient_data_for_pdf = {
            'возраст': age,
            'пол': gender,
        }
        if st.button("📄 Скачать PDF отчет для пациента", use_container_width=True):
            with st.spinner("Генерация PDF..."):
                filename = f"dental_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                pdf_path = generate_pdf_report(
                    results=results,
                    patient_data=patient_data_for_pdf,
                    patient_name=patient_name if patient_name else "Пациент",
                    filename=filename
                )
                with open(pdf_path, 'rb') as f:
                    st.download_button(
                        label="📎 Скачать PDF",
                        data=f.read(),
                        file_name=filename,
                        mime="application/pdf",
                        use_container_width=True
                    )

    # Кнопка для нового пациента
    st.markdown("---")
    if st.button("🔄 Новый пациент", use_container_width=True):
        st.session_state.current_results = None
        st.session_state.patient_name = ""
        st.rerun()

# ============================================
# БОКОВАЯ ПАНЕЛЬ
# ============================================

with st.sidebar:
    st.markdown("### 🏥 О приложении")
    st.markdown("""
    **Стоматологический помощник** использует ML модели.

    | Показатель | Модель |
    |------------|--------|
    | 🦷 КПУ | Gradient Boosting |
    | 🦷 Пародонтит | Random Forest |
    | 🔥 Рефлюкс | Gradient Boosting |
    | 💧 Фтор в моче | Ridge |
    """)

    st.markdown("---")
    st.markdown("### 📊 Статистика сессии")

    total_predictions = len(st.session_state.history)
    st.metric("📋 Всего прогнозов", total_predictions)

    if total_predictions > 0:
        avg_kpu = np.mean([h['kpu'] for h in st.session_state.history])
        st.metric("📈 Средний КПУ", f"{avg_kpu:.1f}")

        high_risk_count = sum(1 for h in st.session_state.history if h.get('parodontit_risk', False))
        st.metric("⚠️ Риск пародонтита", f"{high_risk_count} из {total_predictions}")

    st.markdown("---")
    st.markdown("### 🗑️ Управление историей")

    # Кнопка очистки истории
    if st.button("🗑️ Очистить всю историю", use_container_width=True):
        st.session_state.history = clear_history()
        st.success("✅ История очищена!")
        st.rerun()

    # Кнопка экспорта в CSV
    if len(st.session_state.history) > 0:
        if st.button("📥 Экспорт в CSV", use_container_width=True):
            filename = export_history_to_csv(st.session_state.history)
            with open(filename, 'r', encoding='utf-8-sig') as f:
                st.download_button(
                    label="📎 Скачать CSV",
                    data=f.read(),
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True
                )
    else:
        st.info("📭 Нет данных для экспорта")

    st.markdown("---")
    st.markdown("### ℹ️ Как понимать результаты")
    st.markdown("""
    **Для рисков (Пародонтит, Рефлюкс):**
    - "Нет риска (90%)" → модель на 90% уверена, что заболевания нет
    - "Есть риск (85%)" → модель на 85% уверена, что заболевание есть

    **Уверенность модели:**
    - >85%: 🟢 высокая
    - 65-85%: 🟡 средняя
    - <65%: 🔴 низкая
    """)

    st.markdown("---")
    st.markdown("**Версия:** 1.1")
