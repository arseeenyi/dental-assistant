"""
Страница входа в систему
"""

import streamlit as st
from utils.auth import login, is_authenticated

# Настройка страницы
st.set_page_config(
    page_title="Вход | Стоматологический помощник",
    page_icon="🔐",
    layout="centered"
)

# Если уже авторизован — перенаправляем на главную
if is_authenticated():
    st.switch_page("streamlit_app.py")
    st.stop()

st.title("🦷 Стоматологический помощник")
st.markdown("### 🔐 Вход в систему")

# Форма входа
with st.form("login_form"):
    username = st.text_input("👤 Логин", placeholder="doctor")
    password = st.text_input("🔒 Пароль", type="password", placeholder="••••••••")
    submitted = st.form_submit_button("Войти", use_container_width=True)

    if submitted:
        if not username or not password:
            st.error("❌ Пожалуйста, заполните все поля")
        elif login(username, password):
            st.success("✅ Вход выполнен успешно!")
            st.rerun()
        else:
            st.error("❌ Неверный логин или пароль")

st.markdown("---")
st.caption("🔒 Для защиты данных используется хеширование паролей (SHA-256)")