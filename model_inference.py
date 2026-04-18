"""
ИНФЕРЕНС МОДЕЛЕЙ ДЛЯ ИНТЕГРАЦИИ В ПРИЛОЖЕНИЕ
Загружает обученные модели и делает предсказания
"""

import joblib
import pandas as pd
import numpy as np


class DentalPredictor:
    """Класс для предсказания стоматологических показателей"""

    def __init__(self, models_path='saved_models/'):
        self.models = {}
        self.metadata = None

        # Загружаем метаданные
        import json
        with open(f'{models_path}/metadata.json', 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

        # Загружаем модели
        for target_name in self.metadata['targets'].keys():
            model_data = joblib.load(f'{models_path}/{target_name}_model.pkl')
            self.models[target_name] = model_data

        print("✅ Модели успешно загружены")
        print(f"   Доступные предсказания: {list(self.models.keys())}")

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