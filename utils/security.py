"""
Модуль обеспечения безопасности данных
Анонимизация, шифрование, управление сессиями
"""

import hashlib
import json
import os
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import streamlit as st

# Файлы для хранения
KEY_FILE = ".encryption_key"
HISTORY_FILE_ENCRYPTED = "history_encrypted.bin"


def is_cloud_deployment():
    """Проверка, запущено ли приложение в облаке Streamlit"""
    # Streamlit Cloud устанавливает эту переменную
    return os.environ.get("STREAMLIT_DEPLOY", "").lower() == "cloud" or \
        "share.streamlit.io" in os.environ.get("STREAMLIT_BROWSER_ADDRESS", "")


def get_or_create_key():
    """Получить или создать ключ шифрования"""
    if is_cloud_deployment():
        # В облаке используем временный ключ (не сохраняем)
        return Fernet.generate_key()

    # Локально храним ключ в файле
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        return key


def encrypt_data(data):
    """Шифрование данных перед сохранением"""
    try:
        key = get_or_create_key()
        cipher = Fernet(key)
        json_str = json.dumps(data, ensure_ascii=False, default=str)
        encrypted = cipher.encrypt(json_str.encode())
        return encrypted.hex()
    except Exception as e:
        print(f"Ошибка шифрования: {e}")
        return None


def decrypt_data(encrypted_hex):
    """Расшифровка данных"""
    if not encrypted_hex:
        return None
    try:
        key = get_or_create_key()
        cipher = Fernet(key)
        encrypted = bytes.fromhex(encrypted_hex)
        decrypted = cipher.decrypt(encrypted)
        return json.loads(decrypted.decode())
    except Exception as e:
        print(f"Ошибка расшифровки: {e}")
        return None


def anonymize_patient_data(data):
    """
    Анонимизация персональных данных
    Удаляет или хеширует чувствительную информацию
    """
    if not data:
        return data

    anonymized = data.copy()

    # Обработка имени пациента
    if 'patient_name' in anonymized:
        original_name = anonymized.get('patient_name')
        if original_name and original_name != "Без имени" and len(original_name) > 1:
            # Создаем анонимный идентификатор
            name_hash = hashlib.sha256(original_name.encode()).hexdigest()[:10]
            anonymized['patient_id'] = f"#{name_hash}"
        else:
            anonymized['patient_id'] = "#anon"
        anonymized['patient_name'] = "Аноним"

    return anonymized


def get_data_retention_days():
    """Срок хранения данных (дней)"""
    if is_cloud_deployment():
        return 1  # В облаке храним только 1 день
    return 30  # Локально храним 30 дней


def cleanup_old_data(history):
    """Удаление старых данных"""
    if not history:
        return []

    retention_days = get_data_retention_days()
    now = datetime.now()
    cutoff = now - timedelta(days=retention_days)

    cleaned = []
    for record in history:
        try:
            record_date_str = record.get('datetime', '')[:10]
            if record_date_str:
                record_date = datetime.strptime(record_date_str, "%Y-%m-%d")
                if record_date >= cutoff:
                    cleaned.append(record)
            else:
                cleaned.append(record)
        except:
            # Если дата не распознана, сохраняем
            cleaned.append(record)

    return cleaned


def add_security_notice():
    """Добавить предупреждение о безопасности в боковую панель"""
    if is_cloud_deployment():
        st.sidebar.warning("""
        🔒 **О конфиденциальности**

        ☁️ Облачная демо-версия

        • Данные не сохраняются на сервере
        • Используйте только для тестирования
        • Для реальной работы требуется локальное развертывание
        """)
    else:
        st.sidebar.info("""
        🔒 **Безопасность данных**

        💻 Локальная версия

        • Данные хранятся в зашифрованном виде
        • История сохраняется 30 дней
        • Рекомендовано для клинического использования
        """)