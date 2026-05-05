"""
Страница поиска по истории прогнозов
Фильтрация, поиск, сортировка
В облачной версии поиск по имени отключён для защиты данных
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.security import is_cloud_deployment

st.set_page_config(
    page_title="Поиск по истории | Стоматологический помощник",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Поиск по истории прогнозов")
st.markdown("Поиск и фильтрация среди всех сохранённых прогнозов")

# Проверяем, облачная ли версия
IS_CLOUD = is_cloud_deployment()

# ============================================
# ЗАГРУЗКА ДАННЫХ
# ============================================

if 'history' not in st.session_state or len(st.session_state.history) == 0:
    st.warning("⚠️ История прогнозов пуста. Сделайте хотя бы один прогноз на главной странице.")
    st.info("📌 Перейдите на главную страницу, введите данные пациента и нажмите «Получить прогноз»")
    st.stop()

# Преобразуем историю в DataFrame
df = pd.DataFrame(st.session_state.history)

# Добавляем patient_id для поиска (если есть)
if 'patient_id' not in df.columns:
    df['patient_id'] = "—"

# Преобразуем даты
df['date'] = pd.to_datetime(df['datetime']).dt.date
df['date_display'] = pd.to_datetime(df['datetime']).dt.strftime("%d.%m.%Y %H:%M")

# ============================================
# ПРЕДУПРЕЖДЕНИЕ ДЛЯ ОБЛАЧНОЙ ВЕРСИИ
# ============================================

if IS_CLOUD:
    st.info("""
    🔒 **Конфиденциальность данных**

    В демонстрационной версии поиск по имени пациента отключён для защиты персональных данных.
    Доступны фильтрация по клиническим параметрам: дата, КПУ, возраст, риски.

    Для полнофункциональной работы с реальными данными используйте локальную версию приложения.
    """)

# ============================================
# ФИЛЬТРЫ
# ============================================

st.markdown("### 📋 Фильтры")

col1, col2, col3 = st.columns(3)

with col1:
    # Поиск по имени (только в локальной версии)
    if not IS_CLOUD:
        search_name = st.text_input(
            "🔍 Поиск по имени пациента",
            placeholder="Введите имя...",
            help="Поиск по части имени"
        )
    else:
        # В облачной версии показываем поиск по ID (анонимный)
        search_id = st.text_input(
            "🔍 ID пациента (анонимный)",
            placeholder="#a1b2c3d4e5",
            help="Введите ID пациента, который был выдан при прогнозе"
        )
        search_name = ""  # отключаем поиск по имени

with col2:
    # Фильтр по периоду
    period_options = {
        "Все время": None,
        "Сегодня": 1,
        "Последние 7 дней": 7,
        "Последние 30 дней": 30,
        "Последние 90 дней": 90
    }
    period = st.selectbox("📅 Период", list(period_options.keys()))

with col3:
    # Сортировка
    sort_options = {
        "По дате (новые сверху)": ("datetime", False),
        "По дате (старые сверху)": ("datetime", True),
        "По КПУ (высокий сверху)": ("kpu", False),
        "По КПУ (низкий сверху)": ("kpu", True),
        "По возрасту (старше сверху)": ("age", False),
        "По возрасту (моложе сверху)": ("age", True)
    }
    sort_by = st.selectbox("📊 Сортировка", list(sort_options.keys()))

# Дополнительные фильтры (расширяемые)
with st.expander("🔧 Дополнительные фильтры"):
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        # Фильтр по КПУ
        st.markdown("**🦷 КПУ**")
        kpu_min = st.slider("КПУ от", min_value=0.0, max_value=30.0, value=0.0, step=0.5, key="kpu_min")
        kpu_max = st.slider("КПУ до", min_value=0.0, max_value=30.0, value=30.0, step=0.5, key="kpu_max")

    with col_f2:
        # Фильтр по возрасту
        st.markdown("**📅 Возраст**")
        age_min = st.slider("Возраст от", min_value=0, max_value=120, value=0, step=5, key="age_min")
        age_max = st.slider("Возраст до", min_value=0, max_value=120, value=120, step=5, key="age_max")

    with col_f3:
        # Фильтр по рискам
        st.markdown("**⚠️ Риски**")
        risk_parodontit = st.selectbox("Риск пародонтита", ["Все", "Есть риск", "Нет риска"])
        risk_reflux = st.selectbox("Риск рефлюкса", ["Все", "Есть риск", "Нет риска"])

# ============================================
# ПРИМЕНЕНИЕ ФИЛЬТРОВ
# ============================================

filtered_df = df.copy()

# Фильтр по имени (только локально)
if not IS_CLOUD and search_name:
    filtered_df = filtered_df[
        filtered_df['patient_name'].str.contains(search_name, case=False, na=False)
    ]

# Фильтр по ID пациента (облачная версия)
if IS_CLOUD and search_id:
    filtered_df = filtered_df[
        filtered_df['patient_id'].str.contains(search_id, case=False, na=False)
    ]

# Фильтр по периоду
if period != "Все время" and period_options[period]:
    days = period_options[period]
    cutoff_date = datetime.now().date() - timedelta(days=days)
    filtered_df = filtered_df[filtered_df['date'] >= cutoff_date]

# Фильтр по КПУ
filtered_df = filtered_df[
    (filtered_df['kpu'] >= kpu_min) &
    (filtered_df['kpu'] <= kpu_max)
    ]

# Фильтр по возрасту
filtered_df = filtered_df[
    (filtered_df['age'] >= age_min) &
    (filtered_df['age'] <= age_max)
    ]

# Фильтр по риску пародонтита
if risk_parodontit != "Все":
    risk_value = risk_parodontit == "Есть риск"
    filtered_df = filtered_df[filtered_df['parodontit_risk'] == risk_value]

# Фильтр по риску рефлюкса
if risk_reflux != "Все":
    risk_value = risk_reflux == "Есть риск"
    filtered_df = filtered_df[filtered_df['reflux_risk'] == risk_value]

# Сортировка
sort_col, sort_ascending = sort_options[sort_by]
filtered_df = filtered_df.sort_values(sort_col, ascending=sort_ascending)

# ============================================
# СТАТИСТИКА
# ============================================

st.markdown("---")
st.markdown("### 📊 Результаты поиска")

col_s1, col_s2, col_s3, col_s4 = st.columns(4)

with col_s1:
    st.metric("📋 Найдено прогнозов", len(filtered_df))

with col_s2:
    if len(filtered_df) > 0:
        avg_kpu = filtered_df['kpu'].mean()
        st.metric("📈 Средний КПУ", f"{avg_kpu:.1f}")
    else:
        st.metric("📈 Средний КПУ", "—")

with col_s3:
    if len(filtered_df) > 0:
        risk_count = filtered_df['parodontit_risk'].sum()
        st.metric("⚠️ Риск пародонтита", f"{risk_count} из {len(filtered_df)}")
    else:
        st.metric("⚠️ Риск пародонтита", "—")

with col_s4:
    if len(filtered_df) > 0:
        reflux_count = filtered_df['reflux_risk'].sum()
        st.metric("🔥 Риск рефлюкса", f"{reflux_count} из {len(filtered_df)}")
    else:
        st.metric("🔥 Риск рефлюкса", "—")

# ============================================
# ТАБЛИЦА РЕЗУЛЬТАТОВ
# ============================================

if len(filtered_df) > 0:
    st.markdown("---")
    st.markdown("### 📋 Список прогнозов")

    # Подготавливаем таблицу для отображения
    display_df = filtered_df.copy()

    # Форматируем колонки
    display_df['Дата'] = display_df['date_display']

    # В зависимости от версии показываем разные колонки
    if IS_CLOUD:
        display_df['ID пациента'] = display_df['patient_id']
    else:
        display_df['Пациент'] = display_df['patient_name']

    display_df['Возраст'] = display_df['age'].astype(int)
    display_df['Пол'] = display_df['gender']
    display_df['КПУ'] = display_df['kpu'].round(1)
    display_df['Пародонтит'] = display_df['parodontit_risk'].map({True: '🔴 Есть риск', False: '🟢 Нет риска'})
    display_df['Рефлюкс'] = display_df['reflux_risk'].map({True: '🔴 Есть риск', False: '🟢 Нет риска'})
    display_df['Фтор'] = display_df['fluorine'].round(2)

    # Выбираем колонки для отображения
    if IS_CLOUD:
        columns_to_show = ['Дата', 'ID пациента', 'Возраст', 'Пол', 'КПУ', 'Пародонтит', 'Рефлюкс', 'Фтор']
    else:
        columns_to_show = ['Дата', 'Пациент', 'Возраст', 'Пол', 'КПУ', 'Пародонтит', 'Рефлюкс', 'Фтор']

    st.dataframe(display_df[columns_to_show], use_container_width=True)

    # ============================================
    # ЭКСПОРТ ОТФИЛЬТРОВАННЫХ ДАННЫХ
    # ============================================

    st.markdown("---")
    st.markdown("### 📥 Экспорт результатов")

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        # Экспорт в CSV
        csv_data = display_df[columns_to_show].to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Скачать результаты (CSV)",
            data=csv_data,
            file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col_e2:
        st.info(f"📋 Найдено записей: {len(filtered_df)}")

else:
    st.warning("😕 По вашему запросу ничего не найдено")
    st.info("💡 Попробуйте изменить условия поиска")

# ============================================
# КРАТКАЯ СТАТИСТИКА ПО ВСЕЙ ИСТОРИИ
# ============================================

with st.expander("📊 Статистика по всей истории"):
    col_stat1, col_stat2, col_stat3 = st.columns(3)

    with col_stat1:
        st.metric("Всего прогнозов", len(df))
        if not IS_CLOUD:
            st.metric("Уникальных пациентов", df['patient_name'].nunique())
        else:
            st.metric("Уникальных пациентов", df['patient_id'].nunique())

    with col_stat2:
        st.metric("Общий средний КПУ", f"{df['kpu'].mean():.1f}")
        st.metric("Максимальный КПУ", f"{df['kpu'].max():.1f}")
        st.metric("Минимальный КПУ", f"{df['kpu'].min():.1f}")

    with col_stat3:
        total_paro_risk = df['parodontit_risk'].sum()
        total_reflux_risk = df['reflux_risk'].sum()
        st.metric("Всего с риском пародонтита", f"{total_paro_risk} ({total_paro_risk / len(df) * 100:.0f}%)")
        st.metric("Всего с риском рефлюкса", f"{total_reflux_risk} ({total_reflux_risk / len(df) * 100:.0f}%)")