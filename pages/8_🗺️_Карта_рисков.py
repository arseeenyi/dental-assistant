"""
Страница интерактивной карты рисков
Визуализация влияния различных факторов на стоматологические показатели
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.risk_map import (
    load_data, get_available_targets, get_target_name,
    get_available_features, calculate_correlations,
    get_impact_level, prepare_heatmap_data
)

st.set_page_config(
    page_title="Карта рисков | Стоматологический помощник",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Интерактивная карта рисков")
st.markdown("Визуализация влияния различных факторов на стоматологические показатели")

# ============================================
# ЗАГРУЗКА ДАННЫХ
# ============================================

df = load_data()

if df is None or len(df) < 5:
    st.warning("⚠️ Недостаточно данных для построения карты рисков. Сделайте хотя бы 5 прогнозов.")
    st.stop()

# ============================================
# БОКОВАЯ ПАНЕЛЬ - НАСТРОЙКИ
# ============================================

with st.sidebar:
    st.markdown("### 🎛️ Настройки")

    # Выбор целевого показателя
    targets = get_available_targets()
    target_names = [get_target_name(t) for t in targets]
    selected_target_name = st.selectbox("🎯 Целевой показатель", target_names)

    # Находим ключ выбранного показателя
    target_map = {get_target_name(t): t for t in targets}
    selected_target = target_map[selected_target_name]

    st.markdown("---")
    st.markdown("### ℹ️ Как читать карту")
    st.markdown("""
    - **🔴 Красный** → сильное влияние
    - **🟡 Жёлтый** → среднее влияние
    - **🟢 Зелёный** → слабое влияние
    - **⚪ Серый** → очень слабое влияние

    *Корреляция > 0.5 считается сильной*
    """)

# ============================================
# ТЕПЛОВАЯ КАРТА
# ============================================

st.markdown("### 📊 Тепловая карта влияния факторов")

# Подготавливаем данные
heatmap_df = prepare_heatmap_data(df)

if not heatmap_df.empty:
    # Создаём сводную таблицу для тепловой карты
    pivot_df = heatmap_df.pivot(index='Показатель', columns='Фактор', values='Влияние').fillna(0)

    # Создаём тепловую карту с Plotly
    fig = px.imshow(
        pivot_df,
        text_auto='.2f',
        aspect="auto",
        color_continuous_scale='RdYlGn_r',
        zmin=0, zmax=1,
        title="Влияние факторов на стоматологические показатели"
    )

    fig.update_layout(
        height=500,
        xaxis_title="Факторы",
        yaxis_title="Показатели",
        font=dict(size=12)
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("📭 Нет данных для построения тепловой карты")

# ============================================
# ДЕТАЛЬНЫЙ АНАЛИЗ ВЫБРАННОГО ПОКАЗАТЕЛЯ
# ============================================

st.markdown("---")
st.markdown(f"### 📈 Детальный анализ: {get_target_name(selected_target)}")

# Расчёт корреляций для выбранного показателя
correlations = calculate_correlations(df, selected_target)

if correlations:
    # Создаём DataFrame для отображения
    corr_df = pd.DataFrame([
        {
            'Фактор': get_available_features().get(f, f),
            'Влияние': v,
            'Уровень': get_impact_level(v)[1],
            'Направление': 'Положительная' if v > 0 else 'Отрицательная'
        }
        for f, v in correlations.items()
    ]).sort_values('Влияние', ascending=False)

    # Отображаем таблицу
    st.dataframe(corr_df, use_container_width=True)

    # График влияния факторов
    fig_bar = px.bar(
        corr_df,
        x='Фактор',
        y='Влияние',
        color='Уровень',
        color_discrete_map={
            '🔴 Сильное': '#e74c3c',
            '🟡 Среднее': '#f39c12',
            '🟢 Слабое': '#27ae60',
            '⚪ Очень слабое': '#95a5a6'
        },
        title=f"Влияние факторов на {get_target_name(selected_target)}",
        labels={'Влияние': 'Сила влияния (корреляция)', 'Фактор': ''}
    )

    fig_bar.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

# ============================================
# ИНТЕРАКТИВНЫЙ АНАЛИЗ ПО ВЫБРАННОМУ ФАКТОРУ
# ============================================

st.markdown("---")
st.markdown("### 🔍 Интерактивный анализ по фактору")

features = get_available_features()
selected_feature_name = st.selectbox("Выберите фактор для анализа", list(features.values()))

# Находим ключ выбранного фактора
feature_map = {v: k for k, v in features.items()}
selected_feature = feature_map[selected_feature_name]

# Категориальные признаки (требуют специальной обработки)
categorical_features = ['gender', 'smoking', 'bruxism', 'endocrine']

if selected_feature in df.columns and selected_target in df.columns:

    if selected_feature in categorical_features:
        # Для категориальных признаков используем boxplot или bar chart
        # Группируем данные
        grouped = df.groupby(selected_feature)[selected_target].agg(['mean', 'std', 'count']).reset_index()

        # Преобразуем значения для читаемости
        if selected_feature == 'gender':
            grouped[selected_feature] = grouped[selected_feature].map({1: 'Мужской', 0: 'Женский'})
        elif selected_feature in ['smoking', 'bruxism', 'endocrine']:
            grouped[selected_feature] = grouped[selected_feature].map({1: 'Да', 0: 'Нет'})

        # Создаём столбчатую диаграмму
        fig_bar_cat = px.bar(
            grouped,
            x=selected_feature,
            y='mean',
            error_y='std',
            title=f"Средний {get_target_name(selected_target)} в зависимости от {selected_feature_name}",
            labels={selected_feature: selected_feature_name, 'mean': get_target_name(selected_target)},
            color=selected_feature,
            color_discrete_sequence=['#3498db', '#e74c3c']
        )
        fig_bar_cat.update_layout(height=500)
        st.plotly_chart(fig_bar_cat, use_container_width=True)

        # Показываем статистику
        st.dataframe(grouped, use_container_width=True)

    else:
        # Для числовых признаков используем scatter plot
        fig_scatter = px.scatter(
            df,
            x=selected_feature,
            y=selected_target,
            title=f"Зависимость {selected_feature_name} от {get_target_name(selected_target)}",
            labels={selected_feature: selected_feature_name, selected_target: get_target_name(selected_target)},
            trendline="ols",
            trendline_color_override="#e74c3c",
            opacity=0.7
        )

        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Статистика
        valid_data = df[[selected_feature, selected_target]].dropna()
        if len(valid_data) > 1:
            corr_value = valid_data[selected_feature].corr(valid_data[selected_target])
            st.info(
                f"📊 Корреляция между {selected_feature_name} и {get_target_name(selected_target)}: **{corr_value:.3f}**")
else:
    st.info(f"📭 Недостаточно данных для анализа фактора {selected_feature_name}")

# ============================================
# ЭКСПОРТ
# ============================================

st.markdown("---")
st.markdown("### 📥 Экспорт данных")

if not heatmap_df.empty:
    csv_data = heatmap_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Скачать матрицу влияния (CSV)",
        data=csv_data,
        file_name="risk_map_data.csv",
        mime="text/csv",
        use_container_width=True
    )