"""
Управление историей прогнозов
Сохранение и загрузка истории в JSON файл
"""

import json
import os

HISTORY_FILE = "history.json"


def load_history():
    """Загрузка истории из файла"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_history(history):
    """Сохранение истории в файл"""
    try:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def add_prediction(history, prediction_data):
    """Добавить новый прогноз в историю"""
    # Добавляем в начало списка (новые сверху)
    history.insert(0, prediction_data)

    # Ограничиваем историю последними 1000 записями
    if len(history) > 1000:
        history = history[:1000]

    # Сохраняем в файл
    save_history(history)

    return history


def clear_history():
    """Очистить всю историю"""
    save_history([])
    return []


def export_history_to_csv(history, filename="history_export.csv"):
    """Экспорт истории в CSV"""
    import pandas as pd
    df = pd.DataFrame(history)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    return filename