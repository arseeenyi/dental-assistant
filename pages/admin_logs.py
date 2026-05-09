"""
Страница просмотра журнала действий (только для администратора)
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth import get_current_user
from utils.audit import get_logs, clear_logs

st.set_page_config(
    page_title="Журнал действий | Стоматологический помощник",
    page_icon="📋",
    layout="wide"
)

# Проверка прав доступа
user = get_current_user()
if not user or user['role'] != 'admin':
    st.error("⛔ Доступ запрещён. Эта страница только для администраторов.")
    st.stop()

st.title("📋 Журнал действий")
st.markdown("Просмотр всех действий пользователей в системе")

# Загружаем логи
logs = get_logs()

if logs:
    # Преобразуем в DataFrame
    df = pd.DataFrame(logs)

    # Переименовываем колонки
    df = df.rename(columns={
        'timestamp': 'Дата и время',
        'user': 'Логин',
        'user_name': 'Пользователь',
        'role': 'Роль',
        'action': 'Действие',
        'details': 'Подробности',
        'ip': 'IP-адрес'
    })

    # Форматируем дату
    if 'Дата и время' in df.columns:
        try:
            df['Дата и время'] = pd.to_datetime(df['Дата и время']).dt.strftime("%d.%m.%Y %H:%M:%S")
        except:
            pass

    # Словарь для понятных названий действий
    action_names = {
        'login': '🔐 Вход',
        'login_failed': '❌ Неудачный вход',
        'logout': '🚪 Выход',
        'predict': '🔮 Прогноз',
        'export_csv': '📥 Экспорт CSV',
        'clear_history': '🗑️ Очистка истории',
        'download_pdf': '📄 Скачивание PDF',
        'clear_logs': '🧹 Очистка логов'
    }
    df['Действие'] = df['Действие'].map(lambda x: action_names.get(x, x))

    # Фильтры
    st.markdown("---")
    st.markdown("### 🔍 Фильтры")

    col1, col2 = st.columns(2)

    with col1:
        # Преобразуем все значения в строки перед сортировкой
        unique_logins = [str(x) for x in df['Логин'].unique().tolist() if x is not None]
        users = ["Все"] + sorted(unique_logins)
        filter_user = st.selectbox("👤 Пользователь", users)

    with col2:
        # Преобразуем все значения в строки перед сортировкой
        unique_actions = [str(x) for x in df['Действие'].unique().tolist() if x is not None]
        actions = ["Все"] + sorted(unique_actions)
        filter_action = st.selectbox("🎯 Действие", actions)

    # Применяем фильтры
    filtered_df = df.copy()
    if filter_user != "Все":
        filtered_df = filtered_df[filtered_df['Логин'] == filter_user]
    if filter_action != "Все":
        filtered_df = filtered_df[filtered_df['Действие'] == filter_action]

    st.caption(f"📊 Найдено записей: {len(filtered_df)}")

    # Отображаем таблицу
    st.markdown("---")
    st.markdown("### 📋 Список действий")
    st.dataframe(filtered_df, use_container_width=True)

    # Экспорт
    st.markdown("---")
    st.markdown("### 📥 Экспорт")

    col1, col2 = st.columns(2)

    with col1:
        csv_data = filtered_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 Экспорт в CSV",
            data=csv_data,
            file_name=f"audit_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        if st.button("🗑️ Очистить все логи", use_container_width=True):
            clear_logs()
            st.success("✅ Логи очищены!")
            st.rerun()

else:
    st.info("📭 Журнал действий пуст")