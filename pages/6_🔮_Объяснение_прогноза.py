"""
Страница объяснения прогнозов (SHAP)
Показывает, какие факторы повлияли на результат
"""

import streamlit as st
import sys
import os

# Добавляем корневую папку в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from model_inference import DentalPredictor

# Настройка страницы
st.set_page_config(
    page_title="Объяснение прогноза | Стоматологический помощник",
    page_icon="🔮",
    layout="wide"
)

st.title("🔮 Объяснение прогноза")
st.markdown("Как каждый фактор повлиял на результат?")

# Проверяем, есть ли данные текущего прогноза
if 'current_results' not in st.session_state or st.session_state.current_results is None:
    st.warning("⚠️ Сначала сделайте прогноз на главной странице")
    st.info(
        "1. Перейдите на главную страницу\n2. Введите данные пациента\n3. Нажмите «Получить прогноз»\n4. Вернитесь сюда для объяснения")
    st.stop()


# Загружаем модели
@st.cache_resource
def load_predictor():
    return DentalPredictor()


predictor = load_predictor()

# Получаем данные последнего пациента
if 'last_patient_data' in st.session_state:
    patient_data = st.session_state.last_patient_data
else:
    # Фолбэк: используем демо-данные
    patient_data = {
        'возраст': st.session_state.get('demo_age', 35),
        'рост': st.session_state.get('demo_height', 170),
        'вес': st.session_state.get('demo_weight', 70),
        'пол': 1 if st.session_state.get('demo_gender', 'Мужской') == 'Мужской' else 0,
        'pH_слюны': st.session_state.get('demo_ph_saliva', 6.8),
        'pH_вода': st.session_state.get('demo_ph_water', 7.0),
        'pH_чай': st.session_state.get('demo_ph_tea', 6.5),
        'фтор_вода': st.session_state.get('demo_fluorine_water', 0.5),
        'фтор_продукты': st.session_state.get('demo_fluorine_products', 10.0),
        'фтор_чай': st.session_state.get('demo_fluorine_tea', 0.5),
        'курение_алкоголь': 1 if st.session_state.get('demo_smoking', 'Нет') == 'Да' else 0,
        'бруксизм': 1 if st.session_state.get('demo_bruxism', 'Нет') == 'Да' else 0,
        'эндокринные': 1 if st.session_state.get('demo_endocrine', 'Нет') == 'Да' else 0,
    }

# Выбор целевой переменной
target = st.selectbox(
    "Выберите показатель для анализа",
    ["КПУ", "Пародонтит", "Рефлюкс", "Фтор в моче"],
    format_func=lambda x: {
        "КПУ": "🦷 КПУ (индекс кариеса)",
        "Пародонтит": "🦷 Пародонтит (риск)",
        "Рефлюкс": "🔥 Рефлюкс (риск)",
        "Фтор в моче": "💧 Фтор в моче"
    }[x]
)

if st.button("🔮 Объяснить прогноз", type="primary", use_container_width=True):
    with st.spinner("Анализ влияния факторов..."):
        try:
            # Получаем объяснение в зависимости от выбранной цели
            if target == "КПУ":
                explanation = predictor.explain_kpu(patient_data)
                prediction_value = explanation.get('prediction', 0)
                base_value = explanation.get('base_value', 0)
                is_regression = True
            elif target == "Пародонтит":
                explanation = predictor.explain_parodontit(patient_data)
                prediction_value = "Есть риск" if explanation.get('prediction', 0) == 1 else "Нет риска"
                base_value = explanation.get('base_value', 0)
                is_regression = False
            elif target == "Рефлюкс":
                explanation = predictor.explain_reflux(patient_data)
                prediction_value = "Есть риск" if explanation.get('prediction', 0) == 1 else "Нет риска"
                base_value = explanation.get('base_value', 0)
                is_regression = False
            else:  # Фтор в моче
                explanation = predictor.explain_fluorine(patient_data)
                prediction_value = explanation.get('prediction', 0)
                base_value = explanation.get('base_value', 0)
                is_regression = True

            if 'error' in explanation:
                st.error(f"❌ {explanation['error']}")
                st.info("💡 Для работы SHAP необходимо установить библиотеку: pip install shap")
            else:
                # Отображаем результат
                st.success(f"✅ Прогноз {target}: **{prediction_value}**")

                # Отображаем влияние факторов
                st.markdown("### 📊 Влияние факторов на прогноз")

                sorted_features = explanation.get('sorted_features', [])
                if sorted_features:
                    # Создаём DataFrame для отображения
                    df_impact = pd.DataFrame(sorted_features, columns=['Фактор', 'Влияние'])
                    df_impact['Влияние'] = df_impact['Влияние'].apply(
                        lambda x: float(x[0]) if isinstance(x, (list, np.ndarray)) else float(x)
                    )

                    # Нормализуем влияние для отображения в процентах
                    max_abs_impact = max(df_impact['Влияние'].abs()) if not df_impact.empty else 1
                    if max_abs_impact == 0:
                        max_abs_impact = 1

                    df_impact['Влияние_норм'] = df_impact['Влияние'] / max_abs_impact * 100

                    df_impact['Направление'] = df_impact['Влияние'].apply(
                        lambda x: '📈 Увеличивает' if x > 0 else ('📉 Уменьшает' if x < 0 else '⚪ Не влияет')
                    )
                    df_impact['Абсолютное влияние'] = df_impact['Влияние'].abs()
                    df_impact = df_impact.sort_values('Абсолютное влияние', ascending=False)

                    st.dataframe(df_impact[['Фактор', 'Влияние', 'Направление']], use_container_width=True)

                    # Визуализация
                    st.markdown("### 📈 Визуализация влияния факторов")
                    st.caption("График показывает относительное влияние каждого фактора (в % от максимального)")

                    fig, ax = plt.subplots(figsize=(10, 6))
                    top_features = df_impact.head(10)

                    # Используем нормализованные значения для отображения
                    display_values = top_features['Влияние_норм'].tolist()
                    colors = ['#e74c3c' if v > 0 else '#3498db' for v in top_features['Влияние']]

                    y_pos = np.arange(len(top_features))
                    ax.barh(y_pos, display_values, color=colors)
                    ax.set_yticks(y_pos)
                    ax.set_yticklabels(top_features['Фактор'])
                    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
                    ax.set_xlabel('Относительное влияние на прогноз (%)')
                    ax.set_title(f'Топ-10 факторов, влияющих на прогноз {target}')

                    # Добавляем подписи значений
                    for i, v in enumerate(display_values):
                        ax.text(v + 1, i, f'{v:.1f}%', va='center', fontsize=9)

                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("Нет данных о влиянии факторов")

        except Exception as e:
            st.error(f"Ошибка при объяснении прогноза: {e}")
            st.info("💡 Попробуйте выбрать другой показатель или сделайте новый прогноз")

# Информация о SHAP
with st.expander("ℹ️ Что такое SHAP и как понимать этот график?"):
    st.markdown("""
    **SHAP** (SHapley Additive exPlanations) — это метод объяснения прогнозов машинного обучения.

    **Как читать график:**
    - 🔴 **Красная полоса** → фактор увеличивает прогноз (повышает риск)
    - 🔵 **Синяя полоса** → фактор уменьшает прогноз (снижает риск)
    - **Длина полосы** → показывает силу влияния фактора (в % от максимального)

    **Пример для КПУ:**
    - Если возраст = 55 лет, это может сильно увеличить прогноз
    - Если pH слюны = 5.8 (кислая), это может увеличить прогноз
    - Если фтор в воде = 1.5 мг/л, это может уменьшить прогноз

    **Примечание:** График показывает относительное влияние. Даже если числовые значения маленькие (0.01-0.02), их относительная важность видна на графике.
    """)