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
from utils.hints import get_tooltip, get_norm_text


# ============================================
# ФУНКЦИЯ ПЛАВНОЙ ПРОКРУТКИ
# ============================================

def scroll_to_results():
    """JavaScript для плавной прокрутки к результатам"""
    st.markdown("""
    <script>
        function scrollToResults() {
            const results = document.querySelector('.results-header');
            if (results) {
                results.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
        setTimeout(scrollToResults, 100);
    </script>
    """, unsafe_allow_html=True)


# ============================================
# НАСТРОЙКА СТРАНИЦЫ
# ============================================

st.set_page_config(
    page_title="Стоматологический помощник",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Определение типа устройства
user_agent = st.context.headers.get('User-Agent', '')
is_mobile = 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent
is_tablet = 'iPad' in user_agent or 'Tablet' in user_agent

if is_mobile:
    st.session_state.device_type = 'mobile'
elif is_tablet:
    st.session_state.device_type = 'tablet'
else:
    st.session_state.device_type = 'desktop'

# Кастомные стили с улучшениями дизайна
st.markdown("""
<style>
    /* ============================================ */
    /* ПОЛЬЗОВАТЕЛЬСКИЕ ШРИФТЫ                     */
    /* ============================================ */

    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,100..900;1,100..900&display=swap');

    html, body, .stApp, .stMarkdown, .stButton, .stTextInput, .stNumberInput {
        font-family: 'Inter', sans-serif;
    }

    /* ============================================ */
    /* ГРАДИЕНТНЫЙ ФОН ДЛЯ ЗАГОЛОВКА               */
    /* ============================================ */

    .main-header {
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #1a5276, #e74c3c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.25rem;
    }
    .sub-header {
        font-size: 0.9rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 1.5rem;
    }

    /* ============================================ */
    /* GLASS-MORPHISM ЭФФЕКТ ДЛЯ КАРТОЧЕК          */
    /* ============================================ */

    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        height: 100%;
        min-height: 220px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        background: rgba(255, 255, 255, 1);
    }

    /* ============================================ */
    /* ИКОНКИ В КАРТОЧКАХ                          */
    /* ============================================ */

    .card-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0.2rem 0;
    }

    /* ============================================ */
    /* ПЛАВАЮЩАЯ ПАНЕЛЬ НАВИГАЦИИ (STICKY SIDEBAR) */
    /* ============================================ */

    .css-1d391kg {
        position: sticky !important;
        top: 0 !important;
        z-index: 999 !important;
    }

    section[data-testid="stSidebar"] {
        position: sticky !important;
        top: 0 !important;
        height: 100vh !important;
    }

    /* ============================================ */
    /* АНИМАЦИЯ ПОЯВЛЕНИЯ РЕЗУЛЬТАТОВ (FADE-IN)    */
    /* ============================================ */

    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .metric-card {
        animation: fadeInUp 0.5s ease-out;
    }

    /* ============================================ */
    /* ПУЛЬСИРУЮЩАЯ АНИМАЦИЯ ДЛЯ КНОПКИ            */
    /* ============================================ */

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }

    .stButton button[kind="primary"] {
        animation: pulse 2s infinite;
    }

    /* ============================================ */
    /* ГРАДИЕНТНЫЕ КНОПКИ                           */
    /* ============================================ */

    .stButton button {
        background: linear-gradient(135deg, #e74c3c, #e67e22) !important;
        border: none !important;
        font-weight: bold !important;
        color: white !important;
        border-radius: 25px !important;
        padding: 8px 24px !important;
        transition: all 0.3s ease !important;
    }

    .stButton button:hover {
        background: linear-gradient(135deg, #c0392b, #d35400) !important;
        transform: scale(1.02);
    }

    /* ============================================ */
    /* ОСТАЛЬНЫЕ СТИЛИ                              */
    /* ============================================ */

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

    /* ============================================ */
    /* ПРОГРЕСС-БАРЫ                               */
    /* ============================================ */

    .progress-bar-container {
        background-color: #ecf0f1;
        border-radius: 10px;
        height: 10px;
        margin: 8px 0;
        overflow: hidden;
    }

    .progress-bar {
        border-radius: 10px;
        height: 100%;
        transition: width 0.5s ease;
    }

    .progress-bar-green {
        background: linear-gradient(90deg, #27ae60, #2ecc71);
    }

    .progress-bar-yellow {
        background: linear-gradient(90deg, #f39c12, #f1c40f);
    }

    .progress-bar-red {
        background: linear-gradient(90deg, #e74c3c, #c0392b);
    }

    .progress-label {
        font-size: 0.75rem;
        color: #7f8c8d;
        margin-top: 4px;
        text-align: center;
    }

    /* ============================================ */
    /* АДАПТАЦИЯ ПОД МОБИЛЬНЫЕ УСТРОЙСТВА           */
    /* ============================================ */

    @media only screen and (max-width: 768px) {
        .main-header {
            font-size: 1.5rem !important;
        }
        .sub-header {
            font-size: 0.8rem !important;
        }

        .stButton button {
            font-size: 16px !important;
            padding: 12px 20px !important;
            min-height: 48px !important;
            width: 100% !important;
        }

        .stNumberInput input, .stTextInput input {
            font-size: 16px !important;
            padding: 12px !important;
            min-height: 44px !important;
        }

        .stSlider {
            padding: 15px 0 !important;
        }

        .stRadio label {
            font-size: 16px !important;
            padding: 8px 12px !important;
        }

        .metric-card {
            margin-bottom: 15px !important;
            min-height: auto !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 4px !important;
            flex-wrap: wrap !important;
        }
        .stTabs [data-baseweb="tab"] {
            font-size: 12px !important;
            padding: 8px 12px !important;
            white-space: nowrap !important;
        }

        .stPlotlyChart {
            height: 350px !important;
        }

        .block-container {
            padding: 1rem !important;
        }
    }

    @media only screen and (min-width: 768px) and (max-width: 1024px) {
        .main-header {
            font-size: 1.8rem !important;
        }
        .stButton button {
            font-size: 15px !important;
            padding: 10px 16px !important;
        }
        .metric-card {
            margin-bottom: 10px !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# ЗАГРУЗКА МОДЕЛЕЙ (Скелетон-загрузка)
# ============================================

@st.cache_resource
def load_predictor():
    with st.spinner("🔄 Загрузка моделей..."):
        predictor = DentalPredictor()
    return predictor


predictor = load_predictor()

if predictor is None:
    st.stop()


# ============================================
# ФУНКЦИИ ДЛЯ КНОПОК "ПРИМЕР" И "ОЧИСТИТЬ"
# ============================================

def set_demo_data():
    """Устанавливает демо-данные в session_state"""
    st.session_state.demo_age = 55
    st.session_state.demo_height = 175
    st.session_state.demo_weight = 85
    st.session_state.demo_gender = "Мужской"
    st.session_state.demo_ph_saliva = 5.8
    st.session_state.demo_ph_water = 6.5
    st.session_state.demo_ph_tea = 6.0
    st.session_state.demo_fluorine_water = 1.2
    st.session_state.demo_fluorine_products = 25.0
    st.session_state.demo_fluorine_tea = 1.5
    st.session_state.demo_smoking = "Да"
    st.session_state.demo_bruxism = "Да"
    st.session_state.demo_endocrine = "Нет"
    st.session_state.patient_name = "Тестовый пациент (риск)"
    st.session_state.demo_mode = True


def clear_form_data():
    """Очищает все поля формы"""
    st.session_state.demo_age = 35
    st.session_state.demo_height = 170
    st.session_state.demo_weight = 70
    st.session_state.demo_gender = "Мужской"
    st.session_state.demo_ph_saliva = 6.8
    st.session_state.demo_ph_water = 7.0
    st.session_state.demo_ph_tea = 6.5
    st.session_state.demo_fluorine_water = 0.5
    st.session_state.demo_fluorine_products = 10.0
    st.session_state.demo_fluorine_tea = 0.5
    st.session_state.demo_smoking = "Нет"
    st.session_state.demo_bruxism = "Нет"
    st.session_state.demo_endocrine = "Нет"
    st.session_state.patient_name = ""
    st.session_state.demo_mode = False


# ============================================
# ИНИЦИАЛИЗАЦИЯ SESSION_STATE
# ============================================

if 'history' not in st.session_state:
    st.session_state.history = load_history()
if 'current_results' not in st.session_state:
    st.session_state.current_results = None
if 'patient_name' not in st.session_state:
    st.session_state.patient_name = ""
if 'demo_mode' not in st.session_state:
    st.session_state.demo_mode = False

# Инициализация значений полей формы
if 'demo_age' not in st.session_state:
    st.session_state.demo_age = 35
if 'demo_height' not in st.session_state:
    st.session_state.demo_height = 170
if 'demo_weight' not in st.session_state:
    st.session_state.demo_weight = 70
if 'demo_gender' not in st.session_state:
    st.session_state.demo_gender = "Мужской"
if 'demo_ph_saliva' not in st.session_state:
    st.session_state.demo_ph_saliva = 6.8
if 'demo_ph_water' not in st.session_state:
    st.session_state.demo_ph_water = 7.0
if 'demo_ph_tea' not in st.session_state:
    st.session_state.demo_ph_tea = 6.5
if 'demo_fluorine_water' not in st.session_state:
    st.session_state.demo_fluorine_water = 0.5
if 'demo_fluorine_products' not in st.session_state:
    st.session_state.demo_fluorine_products = 10.0
if 'demo_fluorine_tea' not in st.session_state:
    st.session_state.demo_fluorine_tea = 0.5
if 'demo_smoking' not in st.session_state:
    st.session_state.demo_smoking = "Нет"
if 'demo_bruxism' not in st.session_state:
    st.session_state.demo_bruxism = "Нет"
if 'demo_endocrine' not in st.session_state:
    st.session_state.demo_endocrine = "Нет"

# ============================================
# ЧТЕНИЕ ПАРАМЕТРОВ ИЗ URL (для кнопки "Пример")
# ============================================

params = st.query_params

if "age" in params:
    st.session_state.demo_age = int(params["age"])
if "gender" in params:
    st.session_state.demo_gender = params["gender"]
if "ph_saliva" in params:
    st.session_state.demo_ph_saliva = float(params["ph_saliva"])
if "fluorine_water" in params:
    st.session_state.demo_fluorine_water = float(params["fluorine_water"])
if "smoking" in params:
    st.session_state.demo_smoking = params["smoking"]
if "bruxism" in params:
    st.session_state.demo_bruxism = params["bruxism"]

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
        key="patient_name_input",
        help="Введите ФИО пациента для сохранения в истории"
    )
    st.session_state.patient_name = patient_name

    # Вкладки для ввода
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Личные данные", "🧪 Лабораторные", "💧 Фтор", "⚕️ Факторы риска"])

    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            age = st.number_input(
                "📅 Возраст (лет)",
                min_value=0, max_value=120,
                value=st.session_state.demo_age,
                step=1,
                key="age_input",
                help=get_tooltip('age')
            )
            st.session_state.demo_age = age
            norm_text = get_norm_text('age', age)
            if norm_text:
                st.caption(norm_text)
        with col2:
            height = st.number_input(
                "📏 Рост (см)",
                min_value=50, max_value=250,
                value=st.session_state.demo_height,
                step=1,
                key="height_input",
                help=get_tooltip('height')
            )
            st.session_state.demo_height = height
            norm_text = get_norm_text('height', height)
            if norm_text:
                st.caption(norm_text)
        with col3:
            weight = st.number_input(
                "⚖️ Вес (кг)",
                min_value=10, max_value=300,
                value=st.session_state.demo_weight,
                step=1,
                key="weight_input",
                help=get_tooltip('weight')
            )
            st.session_state.demo_weight = weight
            norm_text = get_norm_text('weight', weight)
            if norm_text:
                st.caption(norm_text)

        gender = st.radio(
            "🚻 Пол",
            ["Мужской", "Женский"],
            horizontal=True,
            index=0 if st.session_state.demo_gender == "Мужской" else 1,
            key="gender_radio",
            help=get_tooltip('gender')
        )
        st.session_state.demo_gender = gender
        gender_value = 1 if gender == "Мужской" else 0
        norm_text = get_norm_text('gender')
        if norm_text:
            st.caption(norm_text)

    with tab2:
        col1, col2, col3 = st.columns(3)
        with col1:
            ph_saliva = st.slider(
                "💧 pH слюны", 5.0, 8.5,
                value=st.session_state.demo_ph_saliva,
                step=0.05,
                help=get_tooltip('ph_saliva'),
                key="ph_saliva_slider"
            )
            st.session_state.demo_ph_saliva = ph_saliva
            norm_text = get_norm_text('ph_saliva', ph_saliva)
            if norm_text:
                st.caption(norm_text)
        with col2:
            ph_water = st.slider(
                "🚰 pH воды", 6.0, 8.5,
                value=st.session_state.demo_ph_water,
                step=0.05,
                help=get_tooltip('ph_water'),
                key="ph_water_slider"
            )
            st.session_state.demo_ph_water = ph_water
            norm_text = get_norm_text('ph_water', ph_water)
            if norm_text:
                st.caption(norm_text)
        with col3:
            ph_tea = st.slider(
                "🍵 pH чая", 5.0, 8.0,
                value=st.session_state.demo_ph_tea,
                step=0.05,
                help=get_tooltip('ph_tea'),
                key="ph_tea_slider"
            )
            st.session_state.demo_ph_tea = ph_tea
            norm_text = get_norm_text('ph_tea', ph_tea)
            if norm_text:
                st.caption(norm_text)

    with tab3:
        col1, col2, col3 = st.columns(3)
        with col1:
            fluorine_water = st.number_input(
                "💧 Фтор в воде (мг/л)",
                min_value=0.0, max_value=5.0,
                value=st.session_state.demo_fluorine_water,
                step=0.1,
                key="fluorine_water_input",
                help=get_tooltip('fluorine_water')
            )
            st.session_state.demo_fluorine_water = fluorine_water
            norm_text = get_norm_text('fluorine_water', fluorine_water)
            if norm_text:
                st.caption(norm_text)
        with col2:
            fluorine_products = st.number_input(
                "🥗 Фтор в продуктах (мг)",
                min_value=0.0, max_value=100.0,
                value=st.session_state.demo_fluorine_products,
                step=1.0,
                key="fluorine_products_input",
                help=get_tooltip('fluorine_products')
            )
            st.session_state.demo_fluorine_products = fluorine_products
            norm_text = get_norm_text('fluorine_products', fluorine_products)
            if norm_text:
                st.caption(norm_text)
        with col3:
            fluorine_tea = st.number_input(
                "🍵 Фтор в чае (мг)",
                min_value=0.0, max_value=10.0,
                value=st.session_state.demo_fluorine_tea,
                step=0.1,
                key="fluorine_tea_input",
                help=get_tooltip('fluorine_tea')
            )
            st.session_state.demo_fluorine_tea = fluorine_tea
            norm_text = get_norm_text('fluorine_tea', fluorine_tea)
            if norm_text:
                st.caption(norm_text)

    with tab4:
        col1, col2, col3 = st.columns(3)
        with col1:
            smoking = st.radio(
                "🚬 Курение/алкоголь",
                ["Нет", "Да"],
                horizontal=True,
                index=0 if st.session_state.demo_smoking == "Нет" else 1,
                key="smoking_radio",
                help=get_tooltip('smoking')
            )
            st.session_state.demo_smoking = smoking
            smoking_value = 1 if smoking == "Да" else 0
            norm_text = get_norm_text('smoking', smoking)
            if norm_text:
                st.caption(norm_text)
        with col2:
            bruxism = st.radio(
                "😬 Бруксизм",
                ["Нет", "Да"],
                horizontal=True,
                index=0 if st.session_state.demo_bruxism == "Нет" else 1,
                key="bruxism_radio",
                help=get_tooltip('bruxism')
            )
            st.session_state.demo_bruxism = bruxism
            bruxism_value = 1 if bruxism == "Да" else 0
            norm_text = get_norm_text('bruxism', bruxism)
            if norm_text:
                st.caption(norm_text)
        with col3:
            endocrine = st.radio(
                "🦋 Эндокринные нарушения",
                ["Нет", "Да"],
                horizontal=True,
                index=0 if st.session_state.demo_endocrine == "Нет" else 1,
                key="endocrine_radio",
                help=get_tooltip('endocrine')
            )
            st.session_state.demo_endocrine = endocrine
            endocrine_value = 1 if endocrine == "Да" else 0
            norm_text = get_norm_text('endocrine', endocrine)
            if norm_text:
                st.caption(norm_text)

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
                    st.session_state.last_patient_data = patient_data

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
                    scroll_to_results()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Ошибка при прогнозе: {e}")

# ============================================
# НИЖНЯЯ ЧАСТЬ - РЕЗУЛЬТАТЫ (АДАПТИВНЫЕ С ПРОГРЕСС-БАРАМИ)
# ============================================

if st.session_state.current_results:
    results = st.session_state.current_results

    st.markdown('<div class="results-header">📊 Результаты прогноза</div>', unsafe_allow_html=True)

    # Подготавливаем данные для карточек (общие для всех устройств)
    kpu = results['КПУ']
    kpu_color = get_kpu_color(kpu)

    # Прогресс-бар для КПУ (максимум 15)
    kpu_percent = min(kpu / 15, 1.0)
    if kpu < 3:
        kpu_bar_class = "progress-bar-green"
        kpu_status_text = "Низкий риск кариеса"
    elif kpu < 7:
        kpu_bar_class = "progress-bar-yellow"
        kpu_status_text = "Средний риск кариеса"
    else:
        kpu_bar_class = "progress-bar-red"
        kpu_status_text = "Высокий риск кариеса"

    paro = results['пародонтит']
    risk_class_paro = "risk-high" if paro['risk'] else "risk-low"
    risk_text_paro = "Есть риск" if paro['risk'] else "Нет риска"
    confidence_paro = paro['risk_percent'] if paro['risk'] else 100 - paro['risk_percent']
    if confidence_paro > 85:
        conf_class_paro = "confidence-high"
        conf_text_paro = "высокая уверенность"
    elif confidence_paro > 65:
        conf_class_paro = "confidence-medium"
        conf_text_paro = "средняя уверенность"
    else:
        conf_class_paro = "confidence-low"
        conf_text_paro = "низкая уверенность"

    reflux = results['рефлюкс']
    risk_class_reflux = "risk-high" if reflux['risk'] else "risk-low"
    risk_text_reflux = "Есть риск" if reflux['risk'] else "Нет риска"
    confidence_reflux = reflux['risk_percent'] if reflux['risk'] else 100 - reflux['risk_percent']
    if confidence_reflux > 85:
        conf_class_reflux = "confidence-high"
        conf_text_reflux = "высокая уверенность"
    elif confidence_reflux > 65:
        conf_class_reflux = "confidence-medium"
        conf_text_reflux = "средняя уверенность"
    else:
        conf_class_reflux = "confidence-low"
        conf_text_reflux = "низкая уверенность"

    fluorine = results['фтор_моча_кг']
    fluorine_color = get_fluorine_color(fluorine)

    # Прогресс-бар для фтора (норма 0.3-1.5)
    if fluorine < 0.3:
        fluorine_percent = fluorine / 0.3
        fluorine_bar_class = "progress-bar-yellow"
        fluorine_status_text = "Низкий уровень фтора"
    elif fluorine < 1.5:
        fluorine_percent = (fluorine - 0.3) / 1.2
        fluorine_bar_class = "progress-bar-green"
        fluorine_status_text = "Оптимальный уровень фтора"
    else:
        fluorine_percent = min((fluorine - 1.5) / 3.5, 1.0)
        fluorine_bar_class = "progress-bar-red"
        fluorine_status_text = "Высокий уровень фтора"

    # Адаптивное расположение в зависимости от типа устройства
    device_type = st.session_state.get('device_type', 'desktop')

    if device_type == 'mobile':
        # На телефоне — карточки вертикально
        st.markdown(f"""
        <div class="metric-card">
            <div class="card-icon">🦷</div>
            <h3 style="margin: 0;">КПУ</h3>
            <div class="metric-value" style="color: {kpu_color}">{kpu:.1f}</div>
            <div class="progress-bar-container">
                <div class="progress-bar {kpu_bar_class}" style="width: {kpu_percent * 100}%;"></div>
            </div>
            <div class="progress-label">{kpu_status_text}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card">
            <div class="card-icon">🦷</div>
            <h3 style="margin: 0;">Пародонтит</h3>
            <div class="metric-value {risk_class_paro}">{risk_text_paro}</div>
            <p style="margin: 5px 0 0 0;">Уверенность модели: {confidence_paro:.0f}%</p>
            <p class="{conf_class_paro}" style="margin: 0;">({conf_text_paro})</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card">
            <div class="card-icon">🔥</div>
            <h3 style="margin: 0;">Рефлюкс</h3>
            <div class="metric-value {risk_class_reflux}">{risk_text_reflux}</div>
            <p style="margin: 5px 0 0 0;">Уверенность модели: {confidence_reflux:.0f}%</p>
            <p class="{conf_class_reflux}" style="margin: 0;">({conf_text_reflux})</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="metric-card" style="margin-top: 1rem;">
            <div class="card-icon">💧</div>
            <h3 style="margin: 0;">Фтор в моче</h3>
            <div class="metric-value" style="color: {fluorine_color}">{fluorine:.2f} мкг/кг</div>
            <div class="progress-bar-container">
                <div class="progress-bar {fluorine_bar_class}" style="width: {fluorine_percent * 100}%;"></div>
            </div>
            <div class="progress-label">{fluorine_status_text}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # На планшете/ПК — карточки горизонтально
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="card-icon">🦷</div>
                <h3 style="margin: 0;">КПУ</h3>
                <div class="metric-value" style="color: {kpu_color}">{kpu:.1f}</div>
                <div class="progress-bar-container">
                    <div class="progress-bar {kpu_bar_class}" style="width: {kpu_percent * 100}%;"></div>
                </div>
                <div class="progress-label">{kpu_status_text}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="card-icon">🦷</div>
                <h3 style="margin: 0;">Пародонтит</h3>
                <div class="metric-value {risk_class_paro}">{risk_text_paro}</div>
                <p style="margin: 5px 0 0 0;">Уверенность модели: {confidence_paro:.0f}%</p>
                <p class="{conf_class_paro}" style="margin: 0;">({conf_text_paro})</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="card-icon">🔥</div>
                <h3 style="margin: 0;">Рефлюкс</h3>
                <div class="metric-value {risk_class_reflux}">{risk_text_reflux}</div>
                <p style="margin: 5px 0 0 0;">Уверенность модели: {confidence_reflux:.0f}%</p>
                <p class="{conf_class_reflux}" style="margin: 0;">({conf_text_reflux})</p>
            </div>
            """, unsafe_allow_html=True)

        # Фтор в моче (отдельная карточка во всю ширину)
        st.markdown(f"""
        <div class="metric-card" style="margin-top: 1rem;">
            <div class="card-icon">💧</div>
            <h3 style="margin: 0;">Фтор в моче</h3>
            <div class="metric-value" style="color: {fluorine_color}">{fluorine:.2f} мкг/кг</div>
            <div class="progress-bar-container">
                <div class="progress-bar {fluorine_bar_class}" style="width: {fluorine_percent * 100}%;"></div>
            </div>
            <div class="progress-label">{fluorine_status_text}</div>
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
# БОКОВАЯ ПАНЕЛЬ - ОБНОВЛЕНА
# ============================================

with st.sidebar:
    # ========== ПРЕДУПРЕЖДЕНИЕ О БЕЗОПАСНОСТИ ==========
    from utils.security import add_security_notice

    add_security_notice()
    st.markdown("---")
    # ========== КОНЕЦ БЛОКА ==========

    # Быстрые действия
    st.markdown("### ⚡ Быстрые действия")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎯 Пример", use_container_width=True):
            st.query_params.update({
                "age": "55",
                "gender": "Мужской",
                "ph_saliva": "5.8",
                "fluorine_water": "1.2",
                "smoking": "Да",
                "bruxism": "Да"
            })
            st.rerun()
    with col2:
        if st.button("🔄 Очистить", use_container_width=True):
            st.query_params.clear()
            st.rerun()

    st.markdown("---")
    st.markdown("### 📋 Недавние пациенты")

    if len(st.session_state.history) > 0:
        recent = st.session_state.history[0]
        st.markdown(f"**Последний:** {recent['patient_name']}")
        st.caption(f"КПУ: {recent['kpu']:.1f} | {recent['datetime'][:10]}")
    else:
        st.caption("Нет истории")

    if st.button("📊 Полная статистика", use_container_width=True):
        st.switch_page("pages/3_📊_Статистика.py")

    if st.button("📊 Корреляционная матрица", use_container_width=True):
        st.switch_page("pages/5_📊_Корреляционная_матрица.py")

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

    if st.button("🗑️ Очистить всю историю", use_container_width=True):
        st.session_state.history = clear_history()
        st.success("✅ История очищена!")
        st.rerun()

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