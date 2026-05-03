"""
Страница корреляционной матрицы
Анализ взаимосвязей между признаками
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Настройка страницы
st.set_page_config(
    page_title="Корреляционная матрица | Стоматологический помощник",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Корреляционная матрица")
st.markdown("Анализ взаимосвязей между клиническими параметрами")

# ============================================
# ПРОВЕРКА НАЛИЧИЯ ДАННЫХ
# ============================================

if 'history' not in st.session_state or len(st.session_state.history) < 3:
    st.warning("⚠️ Недостаточно данных для построения матрицы. Сделайте хотя бы 3 прогноза.")
    st.info("📌 Перейдите на главную страницу и сделайте несколько прогнозов")
    st.stop()

# Преобразуем историю в DataFrame
df = pd.DataFrame(st.session_state.history)

# ============================================
# ВЫБОР ПРИЗНАКОВ ДЛЯ КОРРЕЛЯЦИИ
# ============================================

st.markdown("### 🔍 Выберите параметры для анализа")

# Список доступных числовых признаков
available_features = {
    'age': '📅 Возраст',
    'kpu': '🦷 КПУ (индекс кариеса)',
    'parodontit_percent': '🦷 Риск пародонтита (%)',
    'reflux_percent': '🔥 Риск рефлюкса (%)',
    'fluorine': '💧 Фтор в моче',
}

# Добавляем дополнительные признаки, если они есть в данных
if 'ph_saliva' in df.columns:
    available_features['ph_saliva'] = '💧 pH слюны'
if 'ph_water' in df.columns:
    available_features['ph_water'] = '🚰 pH воды'
if 'ph_tea' in df.columns:
    available_features['ph_tea'] = '🍵 pH чая'
if 'fluorine_water' in df.columns:
    available_features['fluorine_water'] = '💧 Фтор в воде'

# Фильтруем только те признаки, которые есть в данных
available = {k: v for k, v in available_features.items() if k in df.columns}

# Мультиселектор для выбора признаков
selected_features = st.multiselect(
    "Выберите параметры для анализа:",
    options=list(available.keys()),
    default=list(available.keys())[:min(5, len(available))],
    format_func=lambda x: available[x]
)

if len(selected_features) < 2:
    st.info("📌 Выберите как минимум 2 параметра для построения матрицы")
    st.stop()

# ============================================
# РАСЧЁТ КОРРЕЛЯЦИОННОЙ МАТРИЦЫ
# ============================================

# Берём только выбранные колонки
df_selected = df[selected_features].copy()

# Переименовываем колонки для красивого отображения
rename_map = {k: available[k] for k in selected_features}
df_selected = df_selected.rename(columns=rename_map)

# Рассчитываем корреляционную матрицу
corr_matrix = df_selected.corr()

# ============================================
# ВИЗУАЛИЗАЦИЯ
# ============================================

st.markdown("---")
st.markdown("### 📈 Тепловая карта корреляций")

# Создаём интерактивную тепловую карту
fig = px.imshow(
    corr_matrix,
    text_auto='.2f',
    aspect="auto",
    color_continuous_scale='RdBu_r',
    zmin=-1, zmax=1,
    title="Корреляционная матрица"
)

fig.update_layout(
    width=800,
    height=600,
    xaxis_title="Параметры",
    yaxis_title="Параметры"
)

st.plotly_chart(fig, use_container_width=True)

# ============================================
# ПОЯСНЕНИЯ К КОРРЕЛЯЦИИ
# ============================================

with st.expander("📖 Как читать корреляционную матрицу"):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **🟢 Положительная корреляция (+1)**
        - Параметры растут вместе
        - Пример: возраст → КПУ
        - Чем выше значение, тем сильнее связь
        """)

    with col2:
        st.markdown("""
        **🔴 Отрицательная корреляция (-1)**
        - Один растёт, другой падает
        - Пример: pH слюны → КПУ
        - Чем ниже значение, тем сильнее связь
        """)

    with col3:
        st.markdown("""
        **⚪ Нулевая корреляция (0)**
        - Связь отсутствует
        - Параметры независимы
        - Изменения никак не связаны
        """)

# ============================================
# ТАБЛИЦА С КОРРЕЛЯЦИЯМИ
# ============================================

st.markdown("---")
st.markdown("### 📋 Таблица корреляций")

# Форматируем для отображения
corr_display = corr_matrix.round(3).copy()
st.dataframe(corr_display, use_container_width=True)

# ============================================
# НАИБОЛЕЕ СИЛЬНЫЕ СВЯЗИ
# ============================================

st.markdown("---")
st.markdown("### 🔗 Наиболее сильные взаимосвязи")

# Находим топ-5 сильных корреляций (исключая диагональ)
corr_values = []
for i in range(len(corr_matrix.columns)):
    for j in range(i + 1, len(corr_matrix.columns)):
        corr_val = corr_matrix.iloc[i, j]
        corr_values.append({
            'Параметр 1': corr_matrix.columns[i],
            'Параметр 2': corr_matrix.columns[j],
            'Коэффициент': f"{corr_val:.3f}",
            'Сила связи': '🔴 Сильная' if abs(corr_val) > 0.7 else
            ('🟡 Средняя' if abs(corr_val) > 0.3 else '🟢 Слабая'),
            'Направление': '📈 Положительная' if corr_val > 0 else '📉 Отрицательная'
        })

corr_df = pd.DataFrame(corr_values)
corr_df = corr_df.sort_values('Коэффициент', key=lambda x: abs(pd.to_numeric(x)), ascending=False).head(10)

st.dataframe(corr_df, use_container_width=True)

# ============================================
# ЭКСПОРТ
# ============================================

st.markdown("---")
st.markdown("### 📥 Экспорт данных")

col1, col2 = st.columns(2)

with col1:
    csv_matrix = corr_matrix.round(3).to_csv()
    st.download_button(
        label="📥 Скачать матрицу корреляций (CSV)",
        data=csv_matrix,
        file_name=f"correlation_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    csv_strong = corr_df.to_csv(index=False)
    st.download_button(
        label="📥 Скачать сильные связи (CSV)",
        data=csv_strong,
        file_name=f"strong_correlations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

# ============================================
# СТАТИСТИКА ПО ДАННЫМ
# ============================================

with st.expander("📊 Статистика по выбранным параметрам"):
    st.dataframe(df_selected.describe(), use_container_width=True)