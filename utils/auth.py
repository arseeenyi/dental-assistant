"""
Модуль аутентификации пользователей
"""

import hashlib
import json
import os
import streamlit as st
from datetime import datetime
from utils.audit import log_action

# Файл с пользователями
USERS_FILE = "data/users.json"
SESSION_TIMEOUT_HOURS = 8


def hash_password(password: str) -> str:
    """Хеширование пароля (SHA-256)"""
    return hashlib.sha256(password.encode()).hexdigest()


def init_users_file():
    """Создание файла пользователей с дефолтными учетками"""
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(USERS_FILE):
        default_users = {
            "doctor": {
                "password_hash": hash_password("doctor123"),
                "full_name": "Врач-стоматолог",
                "role": "doctor",
                "created_at": datetime.now().isoformat()
            },
            "admin": {
                "password_hash": hash_password("admin123"),
                "full_name": "Главный врач",
                "role": "admin",
                "created_at": datetime.now().isoformat()
            }
        }
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_users, f, ensure_ascii=False, indent=2)
        print("✅ Создан файл пользователей с учетными записями по умолчанию")


def load_users() -> dict:
    """Загрузка списка пользователей"""
    init_users_file()
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def authenticate(username: str, password: str) -> dict:
    """Проверка логина и пароля"""
    users = load_users()

    if username not in users:
        return None

    password_hash = hash_password(password)

    if users[username]["password_hash"] == password_hash:
        return {
            "username": username,
            "full_name": users[username]["full_name"],
            "role": users[username]["role"],
            "authenticated": True
        }

    return None


def login(username: str, password: str) -> bool:
    """Выполнить вход"""
    user = authenticate(username, password)
    if user:
        st.session_state.authenticated = True
        st.session_state.username = user["username"]
        st.session_state.full_name = user["full_name"]
        st.session_state.role = user["role"]
        st.session_state.login_time = datetime.now().isoformat()
        log_action("login", f"Успешный вход: {username}")
        return True
    else:
        log_action("login_failed", f"Неудачная попытка входа: {username}")
        return False


def logout():
    """Выход из системы"""
    username = st.session_state.get('username', 'unknown')
    log_action("logout", f"Выход из системы: {username}")
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.full_name = None
    st.session_state.role = None
    st.session_state.login_time = None


def is_authenticated() -> bool:
    """Проверка, авторизован ли пользователь"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        return False

    # Проверка времени сессии
    if st.session_state.authenticated and 'login_time' in st.session_state:
        try:
            login_time = datetime.fromisoformat(st.session_state.login_time)
            time_diff = (datetime.now() - login_time).total_seconds() / 3600
            if time_diff > SESSION_TIMEOUT_HOURS:
                logout()
                return False
        except:
            pass

    return st.session_state.authenticated


def get_current_user() -> dict:
    """Получение данных текущего пользователя"""
    if is_authenticated():
        return {
            "username": st.session_state.get("username"),
            "full_name": st.session_state.get("full_name"),
            "role": st.session_state.get("role")
        }
    return None


def require_auth():
    """Защита страницы (перенаправление на логин)"""
    if not is_authenticated():
        st.switch_page("pages/login.py")
        st.stop()


def add_user(username: str, password: str, full_name: str, role: str = "doctor"):
    """Добавление нового пользователя (только для админа)"""
    users = load_users()
    users[username] = {
        "password_hash": hash_password(password),
        "full_name": full_name,
        "role": role,
        "created_at": datetime.now().isoformat()
    }
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    return True


def delete_user(username: str):
    """Удаление пользователя"""
    if username in ["doctor", "admin"]:
        return False  # Нельзя удалить дефолтных
    users = load_users()
    if username in users:
        del users[username]
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
        return True
    return False