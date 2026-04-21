"""
Массовый импорт пациентов из Excel
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from model_inference import DentalPredictor
from utils.history_manager import add_prediction

st.set_page_config(
    page_title="Массовый импорт",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Массовый импорт пациентов")
st.markdown("Загрузите Excel файл с данными пациентов и получите прогнозы для всех сразу")


# Загрузка моделей
@st.cache_resource
def load_predictor():
    try:
        return DentalPredictor()
    except Exception as e:
        st.error(f"Ошибка загрузки моделей: {e}")
        return None


predictor = load_predictor()

if predictor is None:
    st.stop()

# ============================================
# ШАБЛОН ФАЙЛА
# ============================================

with st.expander("📋 Пример формата файла"):
    st.markdown("""
    **Excel файл должен содержать следующие колонки:**

    | Колонка | Описание | Пример |
    |---------|----------|--------|
    | patient_name | Имя пациента | Иванов Иван |
    | возраст | Возраст (лет) | 45 |
    | рост | Рост (см) | 175 |
    | вес | Вес (кг) | 80 |
    | пол | Пол | Мужской / Женский |
    | pH_слюны | pH слюны | 6.8 |
    | pH_вода | pH воды | 7.0 |
    | фтор_вода | Фтор в воде (мг/л) | 0.5 |
    | курение_алкоголь | Курение/алкоголь | Да / Нет |
    | бруксизм | Бруксизм | Да / Нет |
    | эндокринные | Эндокринные нарушения | Да / Нет |
    """)

    # Создаем пример файла
    sample_data = {
        'patient_name': ['Иванов Иван', 'Петрова Анна'],
        'возраст': [45, 35],
        'рост': [175, 165],
        'вес': [80, 60],
        'пол': ['Мужской', 'Женский'],
        'pH_слюны': [6.5, 7.0],
        'pH_вода': [7.0, 7.2],
        'фтор_вода': [0.5, 0.8],
        'курение_алкоголь': ['Да', 'Нет'],
        'бруксизм': ['Нет', 'Да'],
        'эндокринные': ['Нет', 'Нет'],
    }
    sample_df = pd.DataFrame(sample_data)

    st.download_button(
        label="📥 Скачать пример файла (Excel)",
        data=sample_df.to_csv(index=False).encode('utf-8-sig'),
        file_name="example_patients.csv",
        mime="text/csv",
        help="Скачайте пример файла для заполнения"
    )

# ============================================
# ЗАГРУЗКА ФАЙЛА
# ============================================

uploaded_file = st.file_uploader(
    "📂 Загрузите Excel или CSV файл",
    type=['xlsx', 'xls', 'csv'],
    help="Поддерживаются форматы .xlsx, .xls, .csv"
)

if uploaded_file is not None:
    try:
        # Читаем файл
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success(f"✅ Файл загружен: {len(df)} пациентов")

        # Показываем предпросмотр
        with st.expander("📋 Предпросмотр загруженных данных"):
            st.dataframe(df.head(10), use_container_width=True)

        # ============================================
        # ОБРАБОТКА
        # ============================================

        if st.button("🚀 Запустить прогноз для всех пациентов", type="primary", use_container_width=True):

            progress_bar = st.progress(0)
            status_text = st.empty()

            results_list = []
            errors_list = []

            # Получаем список признаков из модели
            first_model = list(predictor.models.values())[0]
            required_features = first_model['feature_names']

            for idx, row in df.iterrows():
                status_text.text(f"Обработка: {idx + 1} из {len(df)} - {row.get('patient_name', 'Без имени')}")

                try:
                    # Формируем данные пациента
                    patient_data = {}

                    # Основные поля
                    patient_data['возраст'] = float(row.get('возраст', 35))
                    patient_data['рост'] = float(row.get('рост', 170))
                    patient_data['вес'] = float(row.get('вес', 70))

                    # Пол
                    gender_val = row.get('пол', 'Мужской')
                    patient_data['пол'] = 1 if gender_val == 'Мужской' else 0

                    # pH
                    patient_data['pH_слюны'] = float(row.get('pH_слюны', 6.8))
                    patient_data['pH_вода'] = float(row.get('pH_вода', 7.0))
                    patient_data['pH_чай'] = float(row.get('pH_чай', 6.5)) if 'pH_чай' in row else 6.5

                    # Фтор
                    patient_data['фтор_вода'] = float(row.get('фтор_вода', 0.5))
                    patient_data['фтор_продукты'] = float(
                        row.get('фтор_продукты', 10.0)) if 'фтор_продукты' in row else 10.0
                    patient_data['фтор_чай'] = float(row.get('фтор_чай', 0.5)) if 'фтор_чай' in row else 0.5

                    # Факторы риска
                    patient_data['курение_алкоголь'] = 1 if row.get('курение_алкоголь', 'Нет') == 'Да' else 0
                    patient_data['бруксизм'] = 1 if row.get('бруксизм', 'Нет') == 'Да' else 0
                    patient_data['эндокринные'] = 1 if row.get('эндокринные', 'Нет') == 'Да' else 0

                    # Добавляем недостающие признаки
                    for feature in required_features:
                        if feature not in patient_data:
                            patient_data[feature] = np.nan

                    # Получаем прогноз
                    results = predictor.predict_all(patient_data)

                    # Сохраняем результат
                    result_row = {
                        'patient_name': row.get('patient_name', 'Без имени'),
                        'возраст': patient_data['возраст'],
                        'пол': 'Мужской' if patient_data['пол'] == 1 else 'Женский',
                        'КПУ': round(results['КПУ'], 2),
                        'пародонтит_риск': 'Есть' if results['пародонтит']['risk'] else 'Нет',
                        'пародонтит_уверенность': f"{results['пародонтит']['risk_percent']:.1f}%",
                        'рефлюкс_риск': 'Есть' if results['рефлюкс']['risk'] else 'Нет',
                        'рефлюкс_уверенность': f"{results['рефлюкс']['risk_percent']:.1f}%",
                        'фтор_моча_кг': round(results['фтор_моча_кг'], 2),
                    }
                    results_list.append(result_row)

                    # Сохраняем в историю
                    history_entry = {
                        'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'patient_name': row.get('patient_name', 'Без имени'),
                        'age': patient_data['возраст'],
                        'gender': 'Мужской' if patient_data['пол'] == 1 else 'Женский',
                        'kpu': results['КПУ'],
                        'parodontit_risk': results['пародонтит']['risk'],
                        'parodontit_percent': results['пародонтит']['risk_percent'],
                        'reflux_risk': results['рефлюкс']['risk'],
                        'reflux_percent': results['рефлюкс']['risk_percent'],
                        'fluorine': results['фтор_моча_кг']
                    }
                    st.session_state.history = add_prediction(st.session_state.history, history_entry)

                except Exception as e:
                    errors_list.append({
                        'patient_name': row.get('patient_name', 'Без имени'),
                        'error': str(e)
                    })

                progress_bar.progress((idx + 1) / len(df))

            status_text.text("✅ Обработка завершена!")

            # ============================================
            # РЕЗУЛЬТАТЫ
            # ============================================

            if results_list:
                st.success(f"✅ Успешно обработано: {len(results_list)} пациентов")

                # Таблица результатов
                results_df = pd.DataFrame(results_list)
                st.subheader("📊 Результаты прогнозов")
                st.dataframe(results_df, use_container_width=True)

                # Кнопка скачивания результатов
                csv_results = results_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 Скачать результаты (Excel)",
                    data=csv_results,
                    file_name=f"predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

                # Краткая статистика
                st.subheader("📈 Краткая статистика")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Средний КПУ", f"{results_df['КПУ'].mean():.1f}")
                with col2:
                    risk_count = results_df[results_df['пародонтит_риск'] == 'Есть'].shape[0]
                    st.metric("Риск пародонтита", f"{risk_count} из {len(results_df)}")
                with col3:
                    reflux_count = results_df[results_df['рефлюкс_риск'] == 'Есть'].shape[0]
                    st.metric("Риск рефлюкса", f"{reflux_count} из {len(results_df)}")

            if errors_list:
                st.warning(f"⚠️ Ошибок при обработке: {len(errors_list)}")
                errors_df = pd.DataFrame(errors_list)
                st.dataframe(errors_df, use_container_width=True)

    except Exception as e:
        st.error(f"❌ Ошибка чтения файла: {e}")

# ============================================
# БОКОВАЯ ПАНЕЛЬ
# ============================================

with st.sidebar:
    st.markdown("### 📊 Массовый импорт")
    st.markdown("""
    **Как использовать:**

    1. Скачайте пример файла
    2. Заполните данными пациентов
    3. Загрузите файл
    4. Нажмите "Запустить прогноз"
    5. Скачайте результаты

    **Поддерживаемые форматы:**
    - Excel (.xlsx, .xls)
    - CSV
    """)