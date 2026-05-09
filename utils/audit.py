"""
Модуль логирования действий пользователей
"""

import json
import os
from datetime import datetime
import streamlit as st

# Файл для хранения логов
AUDIT_LOG_FILE = "data/audit_log.json"
MAX_LOG_SIZE = 10000  # Максимальное количество записей


def init_audit_file():
    """Инициализация файла логов"""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(AUDIT_LOG_FILE):
        with open(AUDIT_LOG_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)


def get_client_ip():
    """Получение IP-адреса пользователя"""
    try:
        # Для Streamlit Cloud
        return st.context.headers.get('X-Forwarded-For', 'unknown')
    except:
        return '127.0.0.1'


def log_action(action: str, details: str = ""):
    """
    Запись действия в лог

    Args:
        action: тип действия (login, logout, predict, export_csv, clear_history, etc.)
        details: подробности действия
    """
    init_audit_file()

    # Получаем информацию о пользователе
    username = st.session_state.get('username', 'unknown')
    full_name = st.session_state.get('full_name', 'unknown')
    role = st.session_state.get('role', 'unknown')

    # Создаём запись
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'user': username,
        'user_name': full_name,
        'role': role,
        'action': action,
        'details': details,
        'ip': get_client_ip()
    }

    # Загружаем существующие логи
    try:
        with open(AUDIT_LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except:
        logs = []

    # Добавляем новую запись
    logs.append(log_entry)

    # Ограничиваем размер лога
    if len(logs) > MAX_LOG_SIZE:
        logs = logs[-MAX_LOG_SIZE:]

    # Сохраняем
    with open(AUDIT_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def get_logs(limit=1000):
    """Получение всех логов"""
    init_audit_file()

    try:
        with open(AUDIT_LOG_FILE, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except:
        return []

    # Разворачиваем (новые сверху)
    logs.reverse()

    return logs[:limit]


def clear_logs():
    """Очистка логов (только для админа)"""
    with open(AUDIT_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f, ensure_ascii=False, indent=2)
    log_action("clear_logs", "Логи очищены")