"""
Модуль для расчёта влияния факторов (карта рисков)
"""

import pandas as pd
import numpy as np
from utils.history_manager import load_history


def load_data():
    """Загрузка исторических данных для анализа"""
    history = load_history()
    if not history:
        return None
    return pd.DataFrame(history)


def get_available_targets():
    """Доступные целевые показатели для анализа"""
    return ['kpu', 'parodontit_risk', 'reflux_risk', 'fluorine']


def get_target_name(target):
    """Человекочитаемое название целевого показателя"""
    names = {
        'kpu': 'КПУ (индекс кариеса)',
        'parodontit_risk': 'Пародонтит (риск)',
        'reflux_risk': 'Рефлюкс (риск)',
        'fluorine': 'Фтор в моче'
    }
    return names.get(target, target)


def get_available_features():
    """Доступные факторы для анализа"""
    return {
        'age': 'Возраст',
        'gender': 'Пол',
        'ph_saliva': 'pH слюны',
        'ph_water': 'pH воды',
        'ph_tea': 'pH чая',
        'fluorine_water': 'Фтор в воде',
        'fluorine_products': 'Фтор в продуктах',
        'fluorine_tea': 'Фтор в чае',
        'smoking': 'Курение/алкоголь',
        'bruxism': 'Бруксизм',
        'endocrine': 'Эндокринные нарушения'
    }


def preprocess_dataframe(df):
    """Преобразование категориальных признаков в числовые"""
    df_processed = df.copy()

    # Пол: Мужской → 1, Женский → 0
    if 'gender' in df_processed.columns:
        df_processed['gender'] = df_processed['gender'].map({'Мужской': 1, 'Женский': 0})

    # Курение: Да → 1, Нет → 0
    if 'smoking' in df_processed.columns:
        df_processed['smoking'] = df_processed['smoking'].map({'Да': 1, 'Нет': 0})

    # Бруксизм: Да → 1, Нет → 0
    if 'bruxism' in df_processed.columns:
        df_processed['bruxism'] = df_processed['bruxism'].map({'Да': 1, 'Нет': 0})

    # Эндокринные: Да → 1, Нет → 0
    if 'endocrine' in df_processed.columns:
        df_processed['endocrine'] = df_processed['endocrine'].map({'Да': 1, 'Нет': 0})

    return df_processed


def calculate_correlations(df, target):
    """Расчёт корреляций факторов с целевым показателем"""
    features = get_available_features()
    correlations = {}

    # Преобразуем категориальные признаки
    df_processed = preprocess_dataframe(df)

    for feature in features.keys():
        if feature in df_processed.columns and target in df_processed.columns:
            # Убираем NaN
            valid_data = df_processed[[feature, target]].dropna()
            if len(valid_data) > 5:
                try:
                    corr = valid_data[feature].corr(valid_data[target])
                    if not np.isnan(corr):
                        correlations[feature] = abs(corr)
                except:
                    pass

    return correlations


def get_impact_level(value):
    """Определение уровня влияния по значению корреляции"""
    if value >= 0.5:
        return "high", "🔴 Сильное"
    elif value >= 0.3:
        return "medium", "🟡 Среднее"
    elif value >= 0.1:
        return "low", "🟢 Слабое"
    else:
        return "very_low", "⚪ Очень слабое"


def prepare_heatmap_data(df):
    """Подготовка данных для тепловой карты"""
    targets = get_available_targets()
    features = get_available_features()

    # Преобразуем категориальные признаки
    df_processed = preprocess_dataframe(df)

    heatmap_data = []

    for target in targets:
        if target in df_processed.columns:
            target_name = get_target_name(target)
            for feature, feature_name in features.items():
                if feature in df_processed.columns:
                    valid_data = df_processed[[feature, target]].dropna()
                    if len(valid_data) > 5:
                        try:
                            corr = valid_data[feature].corr(valid_data[target])
                            if not np.isnan(corr):
                                heatmap_data.append({
                                    'Показатель': target_name,
                                    'Фактор': feature_name,
                                    'Влияние': abs(corr),
                                    'Направление': 'Положительная' if corr > 0 else 'Отрицательная'
                                })
                        except:
                            pass

    return pd.DataFrame(heatmap_data)