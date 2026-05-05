"""
ИНФЕРЕНС МОДЕЛЕЙ ДЛЯ ИНТЕГРАЦИИ В ПРИЛОЖЕНИЕ
Загружает обученные модели и делает предсказания
"""

import joblib
import pandas as pd
import numpy as np
import os
import streamlit as st


class DentalPredictor:
    """Класс для предсказания стоматологических показателей"""

    def __init__(self, models_path='saved_models/'):
        self.models = {}
        self.metadata = None
        self._kpu_train_sample = None
        self._parodontit_train_sample = None
        self._reflux_train_sample = None
        self._fluorine_train_sample = None

        # Загружаем метаданные
        import json
        with open(f'{models_path}/metadata.json', 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

        # Загружаем модели
        for target_name in self.metadata['targets'].keys():
            model_data = joblib.load(f'{models_path}/{target_name}_model.pkl')
            self.models[target_name] = model_data

        # Загружаем сохранённые обучающие данные для SHAP (если есть)
        self._load_training_samples(models_path)

        print("✅ Модели успешно загружены")
        print(f"   Доступные предсказания: {list(self.models.keys())}")

    def _load_training_samples(self, models_path):
        """Загрузка сохранённых обучающих выборок для SHAP"""
        try:
            # Пытаемся загрузить сохранённые обучающие данные
            sample_files = {
                'КПУ': 'kpu_train_sample.pkl',
                'пародонтит': 'parodontit_train_sample.pkl',
                'рефлюкс': 'reflux_train_sample.pkl',
                'фтор_моча_кг': 'fluorine_train_sample.pkl'
            }
            for target, filename in sample_files.items():
                filepath = f'{models_path}/{filename}'
                if os.path.exists(filepath):
                    sample = joblib.load(filepath)
                    setattr(self, f'_{target}_train_sample', sample)
        except Exception as e:
            print(f"SHAP обучающие выборки не загружены: {e}")

    def preprocess_input(self, input_data, model_info):
        """Предобработка входных данных"""
        # Создаем DataFrame с нужными колонками
        df = pd.DataFrame([input_data]) if isinstance(input_data, dict) else input_data

        # Проверяем наличие всех признаков
        missing_cols = set(model_info['feature_names']) - set(df.columns)
        if missing_cols:
            for col in missing_cols:
                df[col] = np.nan

        # Берем только нужные колонки
        df = df[model_info['feature_names']]

        # Заполняем пропуски
        df_imputed = model_info['imputer'].transform(df)

        # Масштабируем
        df_scaled = model_info['scaler'].transform(df_imputed)

        return df_scaled

    def predict_kpu(self, patient_data):
        """Предсказание КПУ (индекс кариеса)"""
        model_info = self.models['КПУ']
        X = self.preprocess_input(patient_data, model_info)
        prediction = model_info['model'].predict(X)[0]
        return round(prediction, 2)

    def predict_parodontit(self, patient_data):
        """Предсказание пародонтита (0/1)"""
        model_info = self.models['пародонтит']
        X = self.preprocess_input(patient_data, model_info)
        prediction = model_info['model'].predict(X)[0]
        probability = model_info['model'].predict_proba(X)[0][1] if hasattr(model_info['model'],
                                                                            'predict_proba') else None
        return {
            'risk': int(prediction),
            'risk_percent': round(probability * 100, 1) if probability else None
        }

    def predict_reflux(self, patient_data):
        """Предсказание рефлюкса (0/1)"""
        model_info = self.models['рефлюкс']
        X = self.preprocess_input(patient_data, model_info)
        prediction = model_info['model'].predict(X)[0]
        probability = model_info['model'].predict_proba(X)[0][1] if hasattr(model_info['model'],
                                                                            'predict_proba') else None
        return {
            'risk': int(prediction),
            'risk_percent': round(probability * 100, 1) if probability else None
        }

    def predict_fluorine(self, patient_data):
        """Предсказание фтора в моче (мкг/кг)"""
        model_info = self.models['фтор_моча_кг']
        X = self.preprocess_input(patient_data, model_info)
        prediction = model_info['model'].predict(X)[0]
        return round(prediction, 2)

    def predict_all(self, patient_data):
        """Предсказание всех показателей"""
        return {
            'КПУ': self.predict_kpu(patient_data),
            'пародонтит': self.predict_parodontit(patient_data),
            'рефлюкс': self.predict_reflux(patient_data),
            'фтор_моча_кг': self.predict_fluorine(patient_data)
        }

    # ============================================
    # SHAP ОБЪЯСНЕНИЯ ПРОГНОЗОВ
    # ============================================

    def _to_scalar(self, value):
        """Преобразует numpy array или список в скалярное значение"""
        if value is None:
            return 0.0
        if isinstance(value, (list, np.ndarray)):
            if len(value) == 0:
                return 0.0
            value = value[0]
        if hasattr(value, 'item'):
            try:
                return float(value.item())
            except:
                return float(value)
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _get_train_sample(self, target_name, X_pred):
        """Получение обучающей выборки для SHAP"""
        sample = getattr(self, f'_{target_name}_train_sample', None)

        # Если нет сохранённой выборки, создаём фейковую
        if sample is None:
            feature_names = self.models[target_name]['feature_names']
            n_features = len(feature_names)
            # Создаём случайную выборку из 50 объектов
            sample = pd.DataFrame(
                np.random.randn(50, n_features),
                columns=feature_names
            )
        return sample

    def explain_kpu(self, patient_data):
        """Объяснение прогноза КПУ (SHAP)"""
        try:
            import shap
        except ImportError:
            return {'error': 'Библиотека shap не установлена'}

        model_info = self.models['КПУ']
        model = model_info['model']

        # Подготавливаем данные
        X_pred = self.preprocess_input(patient_data, model_info)
        X_pred_df = pd.DataFrame(X_pred, columns=model_info['feature_names'])

        # Получаем обучающую выборку для фона
        X_train_sample = self._get_train_sample('КПУ', X_pred_df)

        # Создаём explainer
        if hasattr(model, 'estimators_') or 'forest' in str(type(model)).lower():
            explainer = shap.TreeExplainer(model)
        else:
            explainer = shap.LinearExplainer(model, X_train_sample)

        # Рассчитываем SHAP значения
        shap_values = explainer.shap_values(X_pred_df)

        # Получаем базовое значение
        if hasattr(explainer, 'expected_value'):
            base_value = explainer.expected_value
            if isinstance(base_value, (list, np.ndarray)):
                base_value = base_value[1] if len(base_value) > 1 else base_value[0]
        else:
            base_value = 0

        # Собираем объяснение для каждого признака
        shap_dict = {}
        for i, name in enumerate(model_info['feature_names']):
            if i < len(shap_values[0] if len(shap_values.shape) > 1 else shap_values):
                val = shap_values[0][i] if len(shap_values.shape) > 1 else shap_values[i]
                shap_dict[name] = self._to_scalar(val)

        # Сортируем по абсолютному значению
        sorted_features = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)

        return {
            'base_value': self._to_scalar(base_value),
            'prediction': self._to_scalar(model.predict(X_pred_df)[0]),
            'shap_values': shap_dict,
            'sorted_features': sorted_features[:10],
            'feature_names': model_info['feature_names']
        }

    def explain_parodontit(self, patient_data):
        """Объяснение прогноза пародонтита (SHAP)"""
        try:
            import shap
        except ImportError:
            return {'error': 'Библиотека shap не установлена'}

        model_info = self.models['пародонтит']
        model = model_info['model']

        # Подготавливаем данные
        X_pred = self.preprocess_input(patient_data, model_info)
        X_pred_df = pd.DataFrame(X_pred, columns=model_info['feature_names'])

        # Получаем обучающую выборку для фона
        X_train_sample = self._get_train_sample('пародонтит', X_pred_df)

        # Создаём explainer
        if hasattr(model, 'estimators_') or 'forest' in str(type(model)).lower():
            explainer = shap.TreeExplainer(model)
        else:
            explainer = shap.LinearExplainer(model, X_train_sample)

        # Рассчитываем SHAP значения
        shap_values = explainer.shap_values(X_pred_df)

        # Для классификации shap_values может быть списком
        if isinstance(shap_values, list):
            shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]

        # Базовое значение
        if hasattr(explainer, 'expected_value'):
            base_value = explainer.expected_value
            if isinstance(base_value, (list, np.ndarray)):
                base_value = base_value[1] if len(base_value) > 1 else base_value[0]
        else:
            base_value = 0

        # Собираем объяснение
        shap_dict = {}
        for i, name in enumerate(model_info['feature_names']):
            if i < len(shap_values[0] if len(shap_values.shape) > 1 else shap_values):
                val = shap_values[0][i] if len(shap_values.shape) > 1 else shap_values[i]
                shap_dict[name] = self._to_scalar(val)

        sorted_features = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)

        prediction = self._to_scalar(model.predict(X_pred_df)[0])
        probability = None
        if hasattr(model, 'predict_proba'):
            prob = model.predict_proba(X_pred_df)[0][1]
            probability = self._to_scalar(prob)

        return {
            'base_value': self._to_scalar(base_value),
            'prediction': int(round(prediction)),
            'probability': probability,
            'shap_values': shap_dict,
            'sorted_features': sorted_features[:10],
            'feature_names': model_info['feature_names']
        }

    def explain_reflux(self, patient_data):
        """Объяснение прогноза рефлюкса (SHAP)"""
        try:
            import shap
        except ImportError:
            return {'error': 'Библиотека shap не установлена'}

        model_info = self.models['рефлюкс']
        model = model_info['model']

        # Подготавливаем данные
        X_pred = self.preprocess_input(patient_data, model_info)
        X_pred_df = pd.DataFrame(X_pred, columns=model_info['feature_names'])

        # Получаем обучающую выборку для фона
        X_train_sample = self._get_train_sample('рефлюкс', X_pred_df)

        # Создаём explainer
        if hasattr(model, 'estimators_') or 'forest' in str(type(model)).lower():
            explainer = shap.TreeExplainer(model)
        else:
            explainer = shap.LinearExplainer(model, X_train_sample)

        # Рассчитываем SHAP значения
        shap_values = explainer.shap_values(X_pred_df)

        if isinstance(shap_values, list):
            shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]

        if hasattr(explainer, 'expected_value'):
            base_value = explainer.expected_value
            if isinstance(base_value, (list, np.ndarray)):
                base_value = base_value[1] if len(base_value) > 1 else base_value[0]
        else:
            base_value = 0

        shap_dict = {}
        for i, name in enumerate(model_info['feature_names']):
            if i < len(shap_values[0] if len(shap_values.shape) > 1 else shap_values):
                val = shap_values[0][i] if len(shap_values.shape) > 1 else shap_values[i]
                shap_dict[name] = self._to_scalar(val)

        sorted_features = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)

        prediction = self._to_scalar(model.predict(X_pred_df)[0])
        probability = None
        if hasattr(model, 'predict_proba'):
            prob = model.predict_proba(X_pred_df)[0][1]
            probability = self._to_scalar(prob)

        return {
            'base_value': self._to_scalar(base_value),
            'prediction': int(round(prediction)),
            'probability': probability,
            'shap_values': shap_dict,
            'sorted_features': sorted_features[:10],
            'feature_names': model_info['feature_names']
        }

    def explain_fluorine(self, patient_data):
        """Объяснение прогноза фтора в моче (SHAP)"""
        try:
            import shap
        except ImportError:
            return {'error': 'Библиотека shap не установлена'}

        model_info = self.models['фтор_моча_кг']
        model = model_info['model']

        # Подготавливаем данные
        X_pred = self.preprocess_input(patient_data, model_info)
        X_pred_df = pd.DataFrame(X_pred, columns=model_info['feature_names'])

        # Получаем обучающую выборку для фона
        X_train_sample = self._get_train_sample('фтор_моча_кг', X_pred_df)

        # Создаём explainer
        if hasattr(model, 'estimators_') or 'forest' in str(type(model)).lower():
            explainer = shap.TreeExplainer(model)
        else:
            explainer = shap.LinearExplainer(model, X_train_sample)

        # Рассчитываем SHAP значения
        shap_values = explainer.shap_values(X_pred_df)

        if hasattr(explainer, 'expected_value'):
            base_value = explainer.expected_value
        else:
            base_value = 0

        shap_dict = {}
        for i, name in enumerate(model_info['feature_names']):
            if i < len(shap_values[0] if len(shap_values.shape) > 1 else shap_values):
                val = shap_values[0][i] if len(shap_values.shape) > 1 else shap_values[i]
                shap_dict[name] = self._to_scalar(val)

        sorted_features = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)

        return {
            'base_value': self._to_scalar(base_value),
            'prediction': self._to_scalar(model.predict(X_pred_df)[0]),
            'shap_values': shap_dict,
            'sorted_features': sorted_features[:10],
            'feature_names': model_info['feature_names']
        }


# Пример использования
if __name__ == "__main__":
    # Загружаем модели
    predictor = DentalPredictor()

    # Пример входных данных (нужны все признаки из feature_names)
    sample_patient = {
        'pH_слюны': 6.97, 'возраст': 35, 'рост': 170, 'вес': 70,
        # ... остальные признаки можно оставить пустыми
    }

    # Делаем предсказание
    results = predictor.predict_all(sample_patient)
    print("\n📊 РЕЗУЛЬТАТЫ ПРЕДСКАЗАНИЯ:")
    print(f"   КПУ: {results['КПУ']}")
    print(
        f"   Пародонтит: {'Есть риск' if results['пародонтит']['risk'] else 'Нет риска'} ({results['пародонтит']['risk_percent']}%)")
    print(
        f"   Рефлюкс: {'Есть риск' if results['рефлюкс']['risk'] else 'Нет риска'} ({results['рефлюкс']['risk_percent']}%)")
    print(f"   Фтор в моче: {results['фтор_моча_кг']} мкг/кг")

    # Пример SHAP объяснения
    print("\n🔮 SHAP ОБЪЯСНЕНИЕ ПРОГНОЗА КПУ:")
    explanation = predictor.explain_kpu(sample_patient)
    if 'error' not in explanation:
        print(f"   Базовое значение: {explanation['base_value']:.2f}")
        print(f"   Прогноз: {explanation['prediction']:.2f}")
        print("   Топ-5 влияющих факторов:")
        for name, value in explanation['sorted_features'][:5]:
            effect = "+" if value > 0 else ""
            print(f"      • {name}: {effect}{value:.3f}")
    else:
        print(f"   {explanation['error']}")