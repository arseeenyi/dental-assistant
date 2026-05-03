"""
ML МОДЕЛИ ДЛЯ СТОМАТОЛОГИЧЕСКОЙ КЛИНИКИ (ИСПРАВЛЕННАЯ ВЕРСИЯ)
Предсказание: КПУ, Пародонтит, Рефлюкс, Фтор в моче
Устранена утечка данных, добавлена защита от переобучения
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib
import json
import os
import warnings

warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import RobustScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor, \
    GradientBoostingClassifier
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score,
    accuracy_score, f1_score, roc_auc_score
)

# Настройки
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

print("=" * 80)
print("ОБУЧЕНИЕ ML МОДЕЛЕЙ ДЛЯ СТОМАТОЛОГИЧЕСКОЙ КЛИНИКИ (ИСПРАВЛЕННАЯ)")
print("=" * 80)

# ============================================
# 1. ЗАГРУЗКА ДАННЫХ
# ============================================

print("\n📂 1. ЗАГРУЗКА ДАННЫХ")

feature_names = {
    1: 'pH_слюны', 2: 'pH_слюны_2', 3: 'pH_мочи_утро', 4: 'pH_мочи_день',
    5: 'pH_мочи_вечер', 6: 'pH_мочи_средняя', 7: 'pH_мочи_утро_2', 8: 'pH_мочи_день_2',
    9: 'pH_мочи_вечер_2', 10: 'pH_мочи_средняя_2', 11: 'возраст', 12: 'рост',
    13: 'вес', 14: 'энергозатраты', 15: 'КПУ', 16: 'фтор_продукты',
    17: 'фтор_белок', 18: 'фтор_жиры', 19: 'фтор_кальций', 20: 'белок_продукты',
    21: 'белок_фтор', 22: 'белок_жиры', 23: 'белок_кальций', 24: 'жиры_продукты',
    25: 'жиры_фтор', 26: 'жиры_белок', 27: 'жиры_кальций', 28: 'кальций_продукты',
    29: 'кальций_фтор', 30: 'кальций_белок', 31: 'кальций_жиры', 32: 'фтор_вода',
    33: 'фтор_воздух', 34: 'рефлюкс', 35: 'курение_алкоголь', 36: 'пародонтит',
    37: 'кариес', 38: 'риск_кариеса', 39: 'бруксизм', 40: 'эндокринные',
    41: 'дней_до_фтор', 42: 'дней_до_жиры', 43: 'дней_до_белки', 44: 'дней_до_кальций',
    45: 'гидрофторид_ПДК', 46: 'фториды_твердые', 47: 'фториды_твердые_ПДК', 48: 'фтор_чай',
    49: 'pH_вода', 50: 'pH_чай', 51: 'пол', 52: 'фтор_моча_кг', 53: 'йод_моча'
}

# Загрузка файла
file_paths = [
    'Данные_для_анализа_готовые.xlsx',
    r'C:\Users\Aрсений\Desktop\Данные_для_анализа_готовые.xlsx',
]

df = None
for path in file_paths:
    if os.path.exists(path):
        print(f"   ✅ Файл найден: {path}")
        df = pd.read_excel(path, header=None, engine='openpyxl')
        break

if df is None:
    print("   ❌ Файл не найден!")
    exit()

df.columns = [feature_names.get(i + 1, f'feature_{i + 1}') for i in range(df.shape[1])]
print(f"   Размер данных: {df.shape[0]} строк × {df.shape[1]} столбцов")

# ============================================
# 2. ОЧИСТКА ДАННЫХ
# ============================================

print("\n🧹 2. ОЧИСТКА ДАННЫХ")


def clean_value(x):
    if pd.isna(x):
        return np.nan
    if isinstance(x, str):
        x = x.strip()
        if x in ['-', '—', '', 'nan', 'NaN', 'None', 'NULL']:
            return np.nan
        x = x.replace(',', '.')
        try:
            return float(x)
        except ValueError:
            return np.nan
    try:
        return float(x)
    except (TypeError, ValueError):
        return np.nan


for col in df.columns:
    df[col] = df[col].apply(clean_value)
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(how='all')
print(f"   После очистки: {df.shape[0]} строк")

# ============================================
# 3. ОПРЕДЕЛЕНИЕ ЦЕЛЕВЫХ ПЕРЕМЕННЫХ (С ИСКЛЮЧЕНИЕМ ПОДОЗРИТЕЛЬНЫХ ПРИЗНАКОВ)
# ============================================

print("\n🎯 3. ОПРЕДЕЛЕНИЕ ЦЕЛЕВЫХ ПЕРЕМЕННЫХ")

targets = {
    'КПУ': {'column': 'КПУ', 'type': 'regression', 'metric': 'R²'},
    'пародонтит': {'column': 'пародонтит', 'type': 'classification', 'metric': 'AUC-ROC'},
    'рефлюкс': {'column': 'рефлюкс', 'type': 'classification', 'metric': 'AUC-ROC'},
    'фтор_моча_кг': {'column': 'фтор_моча_кг', 'type': 'regression', 'metric': 'R²'}
}

# ⚠️ ВАЖНО: Исключаем признаки, которые могут быть следствием, а не причиной
# (предотвращаем утечку данных)
suspicious_features = [
    # Соотношения, которые могут вычисляться из целевых переменных
    'кальций_фтор', 'кальций_белок', 'кальций_жиры',
    'белок_фтор', 'белок_жиры', 'белок_кальций',
    'жиры_фтор', 'жиры_белок', 'жиры_кальций',
    'фтор_белок', 'фтор_жиры', 'фтор_кальций',
    # Дубликаты целевых
    'кариес', 'риск_кариеса'
]

# Базовые признаки (только первичные измерения)
base_features = [
    'pH_слюны', 'pH_слюны_2', 'pH_мочи_утро', 'pH_мочи_день',
    'pH_мочи_вечер', 'pH_мочи_средняя', 'pH_мочи_утро_2', 'pH_мочи_день_2',
    'pH_мочи_вечер_2', 'pH_мочи_средняя_2', 'возраст', 'рост', 'вес',
    'энергозатраты', 'фтор_продукты', 'белок_продукты', 'жиры_продукты',
    'кальций_продукты', 'фтор_вода', 'фтор_воздух', 'фтор_чай',
    'курение_алкоголь', 'бруксизм', 'эндокринные', 'пол',
    'дней_до_фтор', 'дней_до_жиры', 'дней_до_белки', 'дней_до_кальций',
    'гидрофторид_ПДК', 'фториды_твердые', 'фториды_твердые_ПДК',
    'pH_вода', 'pH_чай', 'йод_моча'
]

# Берем только те признаки, которые есть в данных
feature_cols = [col for col in base_features if col in df.columns]

print(f"   Исключено подозрительных признаков: {len(suspicious_features)}")
print(f"   Оставлено признаков: {len(feature_cols)}")
print(f"   Признаки: {feature_cols[:10]}...")

# ============================================
# 4. ФУНКЦИЯ ПРЕДОБРАБОТКИ
# ============================================

print("\n🔧 4. ПРЕДОБРАБОТКА ДАННЫХ")


def preprocess_data(df, feature_cols, target_name, target_type):
    data = df.dropna(subset=[target_name])

    if len(data) < 20:
        print(f"   ⚠️ Недостаточно данных для {target_name}: {len(data)}")
        return None, None, None, None

    X = data[feature_cols].copy()
    y = data[target_name].copy()

    if target_type == 'classification':
        y = (y > 0.5).astype(int)

    # Только числовые колонки
    numeric_cols = X.select_dtypes(include=[np.number]).columns
    X = X[numeric_cols]

    # Заполняем пропуски
    imputer = SimpleImputer(strategy='median')
    X_imputed = imputer.fit_transform(X)
    X_imputed = pd.DataFrame(X_imputed, columns=X.columns)

    # Масштабирование
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X_imputed)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

    return X_scaled, y, imputer, scaler


# Проверяем данные
valid_targets = {}
for target_name, info in targets.items():
    X, y, imputer, scaler = preprocess_data(df, feature_cols, target_name, info['type'])
    if X is not None:
        valid_targets[target_name] = info
        if info['type'] == 'classification':
            class_dist = y.value_counts().to_dict()
            print(f"   ✅ {target_name}: n={len(X)}, классы 0:{class_dist.get(0, 0)}, 1:{class_dist.get(1, 0)}")
        else:
            print(f"   ✅ {target_name}: n={len(X)}, диапазон=[{y.min():.2f}, {y.max():.2f}]")

if len(valid_targets) == 0:
    print("❌ Нет данных для обучения!")
    exit()

# ============================================
# 5. ОПРЕДЕЛЕНИЕ МОДЕЛЕЙ (С ОГРАНИЧЕНИЯМИ)
# ============================================

print("\n🤖 5. ОПРЕДЕЛЕНИЕ МОДЕЛЕЙ")

# Регрессионные модели с ограничениями
regression_models = {
    'Linear Regression': LinearRegression(),
    'Ridge': Ridge(alpha=1.0, random_state=RANDOM_STATE),
    'Lasso': Lasso(alpha=0.01, random_state=RANDOM_STATE, max_iter=10000),
    'Random Forest': RandomForestRegressor(
        n_estimators=50,
        max_depth=5,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=RANDOM_STATE,
        n_jobs=-1
    ),
    'Gradient Boosting': GradientBoostingRegressor(
        n_estimators=50,
        max_depth=3,
        learning_rate=0.05,
        random_state=RANDOM_STATE
    )
}

# Классификационные модели с ограничениями
classification_models = {
    'Logistic Regression': LogisticRegression(C=0.1, random_state=RANDOM_STATE, max_iter=1000),
    'Random Forest': RandomForestClassifier(
        n_estimators=50,
        max_depth=4,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=RANDOM_STATE,
        n_jobs=-1
    ),
    'Gradient Boosting': GradientBoostingClassifier(
        n_estimators=50,
        max_depth=3,
        learning_rate=0.05,
        random_state=RANDOM_STATE
    )
}

print(f"   Регрессионных моделей: {len(regression_models)}")
print(f"   Классификационных моделей: {len(classification_models)}")

# ============================================
# 6. ОБУЧЕНИЕ И ОЦЕНКА
# ============================================

print("\n📊 6. ОБУЧЕНИЕ И ОЦЕНКА МОДЕЛЕЙ")
print("-" * 80)

results = {}
best_models = {}

for target_name, info in valid_targets.items():
    print(f"\n🎯 ОБУЧЕНИЕ ДЛЯ: {target_name}")

    X, y, imputer, scaler = preprocess_data(df, feature_cols, target_name, info['type'])
    if X is None:
        continue

    # Разделение
    stratify = y if info['type'] == 'classification' else None
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RANDOM_STATE, stratify=stratify
    )

    print(f"   Train: {len(X_train)}, Test: {len(X_test)}")

    models = regression_models if info['type'] == 'regression' else classification_models
    target_results = []

    for model_name, model in models.items():
        try:
            if info['type'] == 'regression':
                cv_scores = cross_val_score(model, X_train, y_train, cv=4, scoring='r2')
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                r2 = r2_score(y_test, y_pred)
                mae = mean_absolute_error(y_test, y_pred)

                target_results.append({
                    'model': model_name,
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std(),
                    'test_R2': r2,
                    'test_MAE': mae,
                    'model_obj': model
                })
                print(f"      ✅ {model_name:20s} | CV R²={cv_scores.mean():.4f} | Test R²={r2:.4f}")

            else:
                cv_scores = cross_val_score(model, X_train, y_train, cv=StratifiedKFold(4), scoring='roc_auc')
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None

                accuracy = accuracy_score(y_test, y_pred)
                f1 = f1_score(y_test, y_pred, zero_division=0)
                auc = roc_auc_score(y_test, y_pred_proba) if y_pred_proba is not None else 0.5

                target_results.append({
                    'model': model_name,
                    'cv_mean': cv_scores.mean(),
                    'cv_std': cv_scores.std(),
                    'test_accuracy': accuracy,
                    'test_f1': f1,
                    'test_auc': auc,
                    'model_obj': model
                })
                print(f"      ✅ {model_name:20s} | CV AUC={cv_scores.mean():.4f} | Test AUC={auc:.4f}")

        except Exception as e:
            print(f"      ❌ {model_name:20s} | Ошибка: {str(e)[:50]}")
            continue

    if not target_results:
        continue

    # Выбор лучшей модели
    if info['type'] == 'regression':
        best = max(target_results, key=lambda x: x['test_R2'])
        print(f"\n   🏆 ЛУЧШАЯ: {best['model']} (Test R²={best['test_R2']:.4f})")
    else:
        best = max(target_results, key=lambda x: x['test_auc'])
        print(f"\n   🏆 ЛУЧШАЯ: {best['model']} (Test AUC={best['test_auc']:.4f})")

    results[target_name] = target_results
    best_models[target_name] = {
        'name': best['model'],
        'model': best['model_obj'],
        'metrics': {k: v for k, v in best.items() if k not in ['model', 'model_obj']}
    }

# ============================================
# 7. СОХРАНЕНИЕ МОДЕЛЕЙ
# ============================================

print("\n💾 7. СОХРАНЕНИЕ МОДЕЛЕЙ")

os.makedirs('saved_models', exist_ok=True)

for target_name, info in best_models.items():
    print(f"\n   Сохранение для {target_name}...")

    X, y, imputer, scaler = preprocess_data(df, feature_cols, target_name, valid_targets[target_name]['type'])

    if X is not None:
        info['model'].fit(X, y)

        model_data = {
            'model': info['model'],
            'imputer': imputer,
            'scaler': scaler,
            'feature_names': X.columns.tolist(),
            'model_type': valid_targets[target_name]['type'],
            'model_name': info['name']
        }

        filename = f'saved_models/{target_name}_model.pkl'
        joblib.dump(model_data, filename)
        print(f"      ✅ Сохранено: {filename}")

# Сохраняем метаданные
metadata = {
    'targets': {k: v for k, v in valid_targets.items()},
    'best_models': {k: v['name'] for k, v in best_models.items()},
    'model_metrics': {k: v['metrics'] for k, v in best_models.items()},
    'feature_names': feature_cols,
    'n_samples': len(df),
    'n_features': len(feature_cols)
}

with open('saved_models/metadata.json', 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print(f"\n   ✅ Сохранено: saved_models/metadata.json")

# ============================================
# 8. ИТОГОВЫЙ ОТЧЕТ
# ============================================

print("\n" + "=" * 80)
print("📋 8. ИТОГОВЫЙ ОТЧЕТ")
print("=" * 80)

print("\n🏆 ЛУЧШИЕ МОДЕЛИ:")
print("-" * 60)

for target_name, info in best_models.items():
    target_info = valid_targets.get(target_name, {})
    print(f"\n📍 {target_name} ({target_info.get('type', 'unknown')})")
    print(f"   Модель: {info['name']}")

    metrics = info['metrics']
    if target_info.get('type') == 'regression':
        print(f"   Test R²: {metrics.get('test_R2', 0):.4f}")
        print(f"   Test MAE: {metrics.get('test_MAE', 0):.4f}")
        print(f"   CV R²: {metrics.get('cv_mean', 0):.4f} (±{metrics.get('cv_std', 0):.4f})")
    else:
        print(f"   Test AUC: {metrics.get('test_auc', 0):.4f}")
        print(f"   Test F1: {metrics.get('test_f1', 0):.4f}")
        print(f"   Test Accuracy: {metrics.get('test_accuracy', 0):.4f}")
        print(f"   CV AUC: {metrics.get('cv_mean', 0):.4f} (±{metrics.get('cv_std', 0):.4f})")

print("\n" + "=" * 80)
print("✅ ОБУЧЕНИЕ ЗАВЕРШЕНО!")
print("=" * 80)
print("\n📁 Модели готовы к интеграции в приложение!")