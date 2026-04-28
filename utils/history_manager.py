"""
Управление историей прогнозов
Сохранение и загрузка истории в зашифрованном виде
"""

import json
import os
import hashlib
import pandas as pd
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

# Конфигурация
HISTORY_FILE_ENCRYPTED = "history_encrypted.bin"
KEY_FILE = ".encryption_key"


# ============================================
# ФУНКЦИИ ШИФРОВАНИЯ
# ============================================

def _get_or_create_key():
    """Получить или создать ключ шифрования"""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as f:
            f.write(key)
        return key


def _encrypt_data(data):
    """Шифрование данных"""
    try:
        key = _get_or_create_key()
        cipher = Fernet(key)
        json_str = json.dumps(data, ensure_ascii=False, default=str)
        encrypted = cipher.encrypt(json_str.encode())
        return encrypted.hex()
    except Exception as e:
        print(f"Ошибка шифрования: {e}")
        return None


def _decrypt_data(encrypted_hex):
    """Расшифровка данных"""
    if not encrypted_hex:
        return None
    try:
        key = _get_or_create_key()
        cipher = Fernet(key)
        encrypted = bytes.fromhex(encrypted_hex)
        decrypted = cipher.decrypt(encrypted)
        return json.loads(decrypted.decode())
    except Exception as e:
        print(f"Ошибка расшифровки: {e}")
        return None


# ============================================
# АНОНИМИЗАЦИЯ
# ============================================

def _anonymize_patient_name(patient_name):
    """Преобразует имя пациента в анонимный ID"""
    if not patient_name or patient_name == "Без имени":
        return "Аноним"
    name_hash = hashlib.sha256(patient_name.encode()).hexdigest()[:10]
    return f"Пациент_{name_hash}"


def _anonymize_record(record):
    """Анонимизация одной записи"""
    if not record:
        return record

    anonymized = record.copy()

    # Анонимизируем имя
    if 'patient_name' in anonymized:
        original_name = anonymized.get('patient_name')
        if original_name and original_name != "Без имени":
            name_hash = hashlib.sha256(original_name.encode()).hexdigest()[:10]
            anonymized['patient_id'] = f"#{name_hash}"
        anonymized['patient_name'] = "Аноним"

    return anonymized


def _cleanup_old_data(history, retention_days=30):
    """Удаление данных старше retention_days дней"""
    if not history:
        return []

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
            cleaned.append(record)

    return cleaned


# ============================================
# ОСНОВНЫЕ ФУНКЦИИ
# ============================================

def load_history():
    """Загрузка истории из зашифрованного файла"""
    if os.path.exists(HISTORY_FILE_ENCRYPTED):
        try:
            with open(HISTORY_FILE_ENCRYPTED, 'r', encoding='utf-8') as f:
                encrypted_hex = f.read().strip()
            decrypted = _decrypt_data(encrypted_hex)
            if decrypted:
                return decrypted
        except Exception as e:
            print(f"Ошибка загрузки истории: {e}")

    return []


def save_history(history):
    """Сохранение истории в зашифрованный файл"""
    if not history:
        return False

    try:
        # Анонимизируем все записи
        anonymized_history = [_anonymize_record(record) for record in history]

        # Очищаем старые данные
        anonymized_history = _cleanup_old_data(anonymized_history)

        # Шифруем и сохраняем
        encrypted = _encrypt_data(anonymized_history)
        if encrypted:
            with open(HISTORY_FILE_ENCRYPTED, 'w', encoding='utf-8') as f:
                f.write(encrypted)
            return True
    except Exception as e:
        print(f"Ошибка сохранения истории: {e}")

    return False


def add_prediction(history, prediction_data):
    """Добавить новый прогноз в историю с анонимизацией"""
    # Анонимизируем запись
    anonymized_entry = _anonymize_record(prediction_data)

    # Добавляем временную метку
    anonymized_entry['anonymized_at'] = datetime.now().isoformat()

    # Добавляем в начало списка
    history.insert(0, anonymized_entry)

    # Ограничиваем историю 500 записями
    if len(history) > 500:
        history = history[:500]

    # Сохраняем
    save_history(history)

    return history


def clear_history():
    """Очистить всю историю"""
    if os.path.exists(HISTORY_FILE_ENCRYPTED):
        os.remove(HISTORY_FILE_ENCRYPTED)
    return []


def export_history_to_csv(history, filename="history_export.csv"):
    """Экспорт истории в CSV с анонимизацией"""
    if not history:
        df = pd.DataFrame(columns=['datetime', 'patient_id', 'age', 'kpu',
                                   'parodontit_risk', 'reflux_risk', 'fluorine'])
    else:
        # Анонимизируем перед экспортом
        anonymized = [_anonymize_record(record) for record in history]
        df = pd.DataFrame(anonymized)

    # Удаляем чувствительные колонки
    cols_to_drop = ['patient_name', 'phone', 'email', 'address']
    for col in cols_to_drop:
        if col in df.columns:
            df = df.drop(columns=[col])

    df.to_csv(filename, index=False, encoding='utf-8-sig')
    return filename