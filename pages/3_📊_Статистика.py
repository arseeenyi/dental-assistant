"""
СТАТИСТИКА ПРОГНОЗОВ
Анализ всех пациентов в истории
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Статистика | Стоматологический помощник",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Статистика прогнозов")
st.markdown("Анализ всех пациентов в истории")

# ============================================
# ЗАГРУЗКА ДАННЫХ ИЗ ИСТОРИИ
# ============================================

if 'history' not in st.session_state or len(st.session_state.history) == 0:
    st.info("📭 Нет данных для статистики. Сделайте хотя бы один прогноз на главной странице.")
    st.stop()

# Преобразуем историю в DataFrame
df_history = pd.DataFrame(st.session_state.history)

# Преобразуем даты
df_history['date'] = pd.to_datetime(df_history['datetime']).dt.date

# ============================================
# ОБЩАЯ СТАТИСТИКА (4 карточки)
# ============================================

st.markdown("### 📈 Общая статистика")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_patients = len(df_history)
    st.metric("👥 Всего прогнозов", total_patients)

with col2:
    avg_kpu = df_history['kpu'].mean()
    st.metric("📊 Средний КПУ", f"{avg_kpu:.1f}")

with col3:
    high_kpu = df_history[df_history['kpu'] > 7].shape[0]
    st.metric("🔴 Высокий КПУ (>7)", f"{high_kpu} из {total_patients}")

with col4:
    risk_parodontit = df_history['parodontit_risk'].sum()
    risk_percent = (risk_parodontit / total_patients) * 100
    st.metric("⚠️ Риск пародонтита", f"{risk_parodontit} ({risk_percent:.0f}%)")

st.markdown("---")

# ============================================
# ГРАФИКИ
# ============================================

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("### 📊 Распределение КПУ")

    # Создаем гистограмму КПУ
    fig_kpu = px.histogram(
        df_history,
        x='kpu',
        nbins=15,
        title="Распределение индекса КПУ",
        labels={'kpu': 'КПУ', 'count': 'Количество пациентов'},
        color_discrete_sequence=['#3498db']
    )
    fig_kpu.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig_kpu, use_container_width=True)

with col_chart2:
    st.markdown("### 📈 Динамика по датам")

    # Группируем по дате
    daily_avg = df_history.groupby('date')['kpu'].mean().reset_index()
    daily_avg = daily_avg.sort_values('date')

    fig_trend = px.line(
        daily_avg,
        x='date',
        y='kpu',
        title="Средний КПУ по дням",
        labels={'date': 'Дата', 'kpu': 'Средний КПУ'},
        markers=True,
        color_discrete_sequence=['#e74c3c']
    )
    fig_trend.update_layout(height=400)
    st.plotly_chart(fig_trend, use_container_width=True)

# ============================================
# РИСКИ (круговые диаграммы)
# ============================================

st.markdown("### 🦷 Распределение рисков")

col_risk1, col_risk2 = st.columns(2)

with col_risk1:
    # Пародонтит
    paro_counts = df_history['parodontit_risk'].value_counts().reset_index()
    paro_counts.columns = ['risk', 'count']
    paro_counts['risk'] = paro_counts['risk'].map({0: 'Нет риска', 1: 'Есть риск'})

    fig_paro = px.pie(
        paro_counts,
        values='count',
        names='risk',
        title="Пародонтит",
        color='risk',
        color_discrete_map={'Нет риска': '#27ae60', 'Есть риск': '#e74c3c'}
    )
    fig_paro.update_layout(height=350)
    st.plotly_chart(fig_paro, use_container_width=True)

with col_risk2:
    # Рефлюкс
    reflux_counts = df_history['reflux_risk'].value_counts().reset_index()
    reflux_counts.columns = ['risk', 'count']
    reflux_counts['risk'] = reflux_counts['risk'].map({0: 'Нет риска', 1: 'Есть риск'})

    fig_reflux = px.pie(
        reflux_counts,
        values='count',
        names='risk',
        title="Рефлюкс",
        color='risk',
        color_discrete_map={'Нет риска': '#27ae60', 'Есть риск': '#e74c3c'}
    )
    fig_reflux.update_layout(height=350)
    st.plotly_chart(fig_reflux, use_container_width=True)

st.markdown("---")

# ============================================
# ТАБЛИЦА ПОСЛЕДНИХ ПРОГНОЗОВ
# ============================================

st.markdown("### 📋 Последние прогнозы")

# Подготавливаем таблицу
display_df = df_history.copy()
display_df = display_df.sort_values('datetime', ascending=False).head(20)

# Форматируем для отображения
display_df['Дата'] = display_df['datetime'].str[:10]
display_df['Пациент'] = display_df['patient_name']
display_df['КПУ'] = display_df['kpu'].round(1)
display_df['Пародонтит'] = display_df['parodontit_risk'].map({0: '🟢 Нет', 1: '🔴 Есть риск'})
display_df['Рефлюкс'] = display_df['reflux_risk'].map({0: '🟢 Нет', 1: '🔴 Есть риск'})
display_df['Фтор'] = display_df['fluorine'].round(2)

# Выводим таблицу
columns_to_show = ['Дата', 'Пациент', 'КПУ', 'Пародонтит', 'Рефлюкс', 'Фтор']
st.dataframe(display_df[columns_to_show], use_container_width=True)

# ============================================
# ЭКСПОРТ СТАТИСТИКИ
# ============================================

st.markdown("---")
st.markdown("### 📥 Экспорт данных")

col_export1, col_export2, col_export3 = st.columns([1, 2, 1])
with col_export2:
    # Кнопка экспорта
    csv_data = df_history.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Экспорт всей статистики в CSV",
        data=csv_data,
        file_name=f"statistics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

st.caption(f"📊 Данные актуальны на {datetime.now().strftime('%d.%m.%Y %H:%M')}")