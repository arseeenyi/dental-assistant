"""
SHAP объяснение прогнозов
Показывает, какие признаки повлияли на результат
"""

import shap
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from typing import Dict, Any, List


# Кэшируем explainer, чтобы не пересоздавать каждый раз
@st.cache_resource
def get_explainer(model, X_train_sample):
    """Создание SHAP explainer для модели"""
    try:
        # Для RandomForest используем TreeExplainer
        if hasattr(model, 'estimators_') or str(type(model)).find('forest') > -1:
            explainer = shap.TreeExplainer(model)
        else:
            # Для линейных моделей (Ridge, Lasso)
            explainer = shap.LinearExplainer(model, X_train_sample)
        return explainer
    except Exception as e:
        st.warning(f"SHAP explainer не создан: {e}")
        return None


def explain_prediction(model, X_train_sample, X_pred) -> Dict[str, Any]:
    """
    Объяснение одного прогноза

    Args:
        model: обученная модель
        X_train_sample: обучающая выборка (для фона)
        X_pred: данные пациента для объяснения

    Returns:
        dict: объяснение с значениями SHAP
    """
    explainer = get_explainer(model, X_train_sample)
    if explainer is None:
        return None

    # Если передан словарь, преобразуем в DataFrame
    if isinstance(X_pred, dict):
        X_pred = pd.DataFrame([X_pred])

    # Рассчитываем SHAP значения
    shap_values = explainer.shap_values(X_pred)

    # Для классификации shap_values может быть списком
    if isinstance(shap_values, list):
        shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]

    # Базовое значение (expected value)
    expected_value = explainer.expected_value
    if isinstance(expected_value, list):
        expected_value = expected_value[1] if len(expected_value) > 1 else expected_value[0]

    # Собираем объяснение для каждого признака
    feature_names = X_pred.columns.tolist()
    shap_dict = {}

    for i, name in enumerate(feature_names):
        if i < len(shap_values[0] if len(shap_values.shape) > 1 else shap_values):
            val = shap_values[0][i] if len(shap_values.shape) > 1 else shap_values[i]
            shap_dict[name] = float(val)

    return {
        'base_value': float(expected_value),
        'shap_values': shap_dict,
        'prediction': float(model.predict(X_pred)[0]),
        'feature_names': feature_names
    }


def plot_shap_waterfall(explanation: Dict[str, Any], figsize=(10, 6)):
    """Создание waterfall графика SHAP"""
    if explanation is None:
        return None

    fig, ax = plt.subplots(figsize=figsize)

    # Сортируем признаки по влиянию
    features = list(explanation['shap_values'].keys())
    values = [explanation['shap_values'][f] for f in features]

    # Сортируем по абсолютному значению
    sorted_idx = np.argsort(np.abs(values))[::-1]
    sorted_features = [features[i] for i in sorted_idx[:10]]  # топ-10
    sorted_values = [values[i] for i in sorted_idx[:10]]

    # Цвета: красный (увеличивает), синий (уменьшает)
    colors = ['#e74c3c' if v > 0 else '#3498db' for v in sorted_values]

    # Горизонтальная бар-диаграмма
    y_pos = np.arange(len(sorted_features))
    ax.barh(y_pos, sorted_values, color=colors)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(sorted_features)
    ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    ax.set_xlabel('Влияние на прогноз (SHAP value)')
    ax.set_title(f'Прогноз: {explanation["prediction"]:.2f}\nБазовое значение: {explanation["base_value"]:.2f}')

    # Добавляем подписи значений
    for i, v in enumerate(sorted_values):
        ax.text(v + (0.05 if v > 0 else -0.2), i, f'{v:+.2f}', va='center', fontsize=9)

    plt.tight_layout()
    return fig


def plot_shap_summary(shap_values, X_train_sample):
    """Summary plot для всех признаков (глобальное объяснение)"""
    if shap_values is None:
        return None

    fig, ax = plt.subplots(figsize=(12, 8))
    shap.summary_plot(shap_values, X_train_sample, show=False)
    plt.tight_layout()
    return fig