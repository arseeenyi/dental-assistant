import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings

warnings.filterwarnings('ignore')

# Настройка стиля графиков
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# ============================================
# 1. ЗАГРУЗКА ДАННЫХ
# ============================================

# Расшифровка признаков (из image.png)
feature_names = {
    1: 'pH_слюны',
    2: 'pH_слюны_2',
    3: 'pH_мочи_утро',
    4: 'pH_мочи_день',
    5: 'pH_мочи_вечер',
    6: 'pH_мочи_средняя',
    7: 'pH_мочи_утро_2',
    8: 'pH_мочи_день_2',
    9: 'pH_мочи_вечер_2',
    10: 'pH_мочи_средняя_2',
    11: 'возраст',
    12: 'рост',
    13: 'вес',
    14: 'энергозатраты',
    15: 'КПУ',
    16: 'фтор_продукты',
    17: 'фтор_белок',
    18: 'фтор_жиры',
    19: 'фтор_кальций',
    20: 'белок_продукты',
    21: 'белок_фтор',
    22: 'белок_жиры',
    23: 'белок_кальций',
    24: 'жиры_продукты',
    25: 'жиры_фтор',
    26: 'жиры_белок',
    27: 'жиры_кальций',
    28: 'кальций_продукты',
    29: 'кальций_фтор',
    30: 'кальций_белок',
    31: 'кальций_жиры',
    32: 'фтор_вода',
    33: 'фтор_воздух',
    34: 'рефлюкс',
    35: 'курение_алкоголь',
    36: 'пародонтит',
    37: 'кариес',
    38: 'риск_кариеса',
    39: 'бруксизм',
    40: 'эндокринные',
    41: 'дней_до_фтор',
    42: 'дней_до_жиры',
    43: 'дней_до_белки',
    44: 'дней_до_кальций',
    45: 'гидрофторид_ПДК',
    46: 'фториды_твердые',
    47: 'фториды_твердые_ПДК',
    48: 'фтор_чай',
    49: 'pH_вода',
    50: 'pH_чай',
    51: 'пол',
    52: 'фтор_моча_кг',
    53: 'йод_моча'
}

# Загружаем данные
df = pd.read_excel(r'C:\Users\Aрсений\Desktop\Данные_для_анализа_готовые.xlsx', header=None, engine='openpyxl')

# Устанавливаем названия столбцов
df.columns = [feature_names.get(i + 1, f'feature_{i + 1}') for i in range(df.shape[1])]

print("=" * 80)
print("ПЕРВИЧНЫЙ АНАЛИЗ МЕДИЦИНСКИХ ДАННЫХ")
print("=" * 80)

print(f"\nРазмер данных: {df.shape[0]} строк x {df.shape[1]} столбцов")
print(f"\nСписок признаков ({len(df.columns)}):")
for i, col in enumerate(df.columns):
    print(f"  {i + 1:2d}. {col}")

# ============================================
# 2. ОБЩАЯ ИНФОРМАЦИЯ О ДАННЫХ
# ============================================

print("\n" + "=" * 80)
print("2. ОБЩАЯ ИНФОРМАЦИЯ О ДАННЫХ")
print("=" * 80)

print("\nТипы данных:")
print(df.dtypes.value_counts())

print("\nСтатистика по пропущенным значениям:")
missing = df.isnull().sum()
missing_pct = (missing / len(df)) * 100
missing_df = pd.DataFrame({'Пропуски': missing, '%': missing_pct})
missing_df = missing_df[missing_df['Пропуски'] > 0].sort_values('Пропуски', ascending=False)
if len(missing_df) > 0:
    print(missing_df)
else:
    print("Пропущенных значений нет")

# ============================================
# 3. ОПИСАТЕЛЬНАЯ СТАТИСТИКА
# ============================================

print("\n" + "=" * 80)
print("3. ОПИСАТЕЛЬНАЯ СТАТИСТИКА")
print("=" * 80)

numeric_cols = df.select_dtypes(include=[np.number]).columns
print(f"\nЧисловых признаков: {len(numeric_cols)}")
print("\nОсновные статистики:")
stats_df = df[numeric_cols].describe().T
stats_df['skewness'] = df[numeric_cols].skew()
stats_df['kurtosis'] = df[numeric_cols].kurtosis()
print(stats_df.round(2).head(20))

# ============================================
# 4. АНАЛИЗ ВЫБРОСОВ
# ============================================

print("\n" + "=" * 80)
print("4. АНАЛИЗ ВЫБРОСОВ (метод IQR)")
print("=" * 80)

outliers_summary = []
for col in numeric_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
    outliers_summary.append({
        'Признак': col,
        'Q1': Q1,
        'Q3': Q3,
        'IQR': IQR,
        'Нижняя_граница': lower_bound,
        'Верхняя_граница': upper_bound,
        'Кол-во_выбросов': len(outliers),
        '%_выбросов': (len(outliers) / len(df)) * 100
    })

outliers_df = pd.DataFrame(outliers_summary)
outliers_df = outliers_df[outliers_df['Кол-во_выбросов'] > 0].sort_values('%_выбросов', ascending=False)
print(outliers_df.head(15).round(2))

# ============================================
# 5. КОРРЕЛЯЦИОННЫЙ АНАЛИЗ
# ============================================

print("\n" + "=" * 80)
print("5. КОРРЕЛЯЦИОННЫЙ АНАЛИЗ")
print("=" * 80)

key_features = ['КПУ', 'фтор_моча_кг', 'йод_моча', 'возраст', 'фтор_вода', 'фтор_чай']
existing_features = [f for f in key_features if f in df.columns]

if len(existing_features) > 1:
    corr_matrix = df[existing_features].corr()
    print("\nКорреляционная матрица ключевых показателей:")
    print(corr_matrix.round(3))

    if 'КПУ' in df.columns:
        print("\nКорреляции с КПУ (индекс кариеса):")
        kpu_corr = df[numeric_cols].corr()['КПУ'].sort_values(ascending=False)
        print(kpu_corr.head(10).round(3))

# ============================================
# 6. ВИЗУАЛИЗАЦИЯ
# ============================================

print("\n" + "=" * 80)
print("6. ПОСТРОЕНИЕ ГРАФИКОВ")
print("=" * 80)

import os

os.makedirs('analysis_plots', exist_ok=True)

# 6.1 Распределение ключевых признаков
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()
plot_features = ['КПУ', 'возраст', 'фтор_моча_кг', 'йод_моча', 'фтор_вода', 'фтор_чай']
plot_features = [f for f in plot_features if f in df.columns]

for i, feature in enumerate(plot_features):
    if i < len(axes):
        sns.histplot(df[feature], kde=True, ax=axes[i], bins=30, color='steelblue')
        axes[i].set_title(f'Распределение: {feature}', fontsize=12, fontweight='bold')
        axes[i].set_xlabel(feature)
        axes[i].set_ylabel('Частота')
        mean_val = df[feature].mean()
        median_val = df[feature].median()
        axes[i].axvline(mean_val, color='red', linestyle='--', label=f'mean={mean_val:.2f}')
        axes[i].axvline(median_val, color='green', linestyle='--', label=f'median={median_val:.2f}')
        axes[i].legend()

plt.suptitle('Распределение ключевых клинических показателей', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('analysis_plots/1_distributions.png', dpi=150, bbox_inches='tight')
plt.show()

# 6.2 Box-plot для выявления выбросов
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()

for i, feature in enumerate(plot_features):
    if i < len(axes):
        sns.boxplot(y=df[feature], ax=axes[i], color='lightcoral')
        axes[i].set_title(f'Box-plot: {feature}', fontsize=12, fontweight='bold')
        axes[i].set_ylabel(feature)

plt.suptitle('Выявление выбросов методом box-plot', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('analysis_plots/2_boxplots.png', dpi=150, bbox_inches='tight')
plt.show()

# 6.3 Корреляционная тепловая карта
if len(numeric_cols) > 1:
    if 'КПУ' in df.columns:
        kpu_corr_abs = df[numeric_cols].corr()['КПУ'].abs().sort_values(ascending=False)
        top_features = kpu_corr_abs.head(15).index.tolist()
    else:
        top_features = numeric_cols[:15]

    fig, ax = plt.subplots(figsize=(14, 12))
    corr_top = df[top_features].corr()
    mask = np.triu(np.ones_like(corr_top, dtype=bool))
    sns.heatmap(corr_top, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
                center=0, square=True, linewidths=0.5, ax=ax,
                cbar_kws={'shrink': 0.8})
    ax.set_title('Корреляционная матрица (топ-15 признаков)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('analysis_plots/3_correlation_heatmap.png', dpi=150, bbox_inches='tight')
    plt.show()

# 6.4 Матрица рассеяния для ключевых признаков
if len(plot_features) >= 3:
    fig = plt.figure(figsize=(12, 10))
    scatter_features = plot_features[:4]
    scatter_df = df[scatter_features].dropna()

    plot_idx = 1
    for i, feature_x in enumerate(scatter_features):
        for j, feature_y in enumerate(scatter_features):
            if i < j:
                plt.subplot(2, 3, plot_idx)
                plt.scatter(scatter_df[feature_x], scatter_df[feature_y], alpha=0.6, c='steelblue')
                plt.xlabel(feature_x)
                plt.ylabel(feature_y)
                z = np.polyfit(scatter_df[feature_x], scatter_df[feature_y], 1)
                p = np.poly1d(z)
                plt.plot(scatter_df[feature_x].sort_values(),
                         p(scatter_df[feature_x].sort_values()),
                         'r--', alpha=0.8)
                corr_val = scatter_df[feature_x].corr(scatter_df[feature_y])
                plt.title(f'corr = {corr_val:.3f}', fontsize=10)
                plot_idx += 1

    plt.suptitle('Матрица рассеяния ключевых показателей', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('analysis_plots/4_scatter_matrix.png', dpi=150, bbox_inches='tight')
    plt.show()

# 6.5 Категориальные признаки (факторы риска)
cat_features = ['рефлюкс', 'курение_алкоголь', 'пародонтит', 'кариес', 'риск_кариеса', 'бруксизм', 'эндокринные', 'пол']
cat_features = [f for f in cat_features if f in df.columns]

if cat_features:
    n_cats = len(cat_features)
    n_cols = 4
    n_rows = (n_cats + n_cols - 1) // n_cols
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 4 * n_rows))
    axes = axes.flatten() if n_rows > 1 else [axes]

    for i, feature in enumerate(cat_features):
        if i < len(axes):
            value_counts = df[feature].value_counts()
            colors = ['#2ecc71', '#e74c3c'] if len(value_counts) == 2 else ['#3498db', '#9b59b6', '#f39c12']
            axes[i].bar(value_counts.index, value_counts.values, color=colors[:len(value_counts)], edgecolor='black')
            axes[i].set_title(f'{feature}', fontsize=11, fontweight='bold')
            axes[i].set_xlabel(feature)
            axes[i].set_ylabel('Количество')
            axes[i].set_xticks(value_counts.index)
            for j, (idx, val) in enumerate(value_counts.items()):
                pct = (val / len(df)) * 100
                axes[i].text(j, val + 0.5, f'{pct:.1f}%', ha='center', fontsize=9)

    for i in range(len(cat_features), len(axes)):
        axes[i].set_visible(False)

    plt.suptitle('Распределение категориальных факторов риска', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('analysis_plots/5_categorical_features.png', dpi=150, bbox_inches='tight')
    plt.show()

# 6.6 Гистограммы всех числовых признаков
n_features = len(numeric_cols)
n_cols = 4
n_rows = (n_features + n_cols - 1) // n_cols

fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5 * n_rows))
axes = axes.flatten() if n_rows > 1 else [axes]

for i, feature in enumerate(numeric_cols):
    if i < len(axes):
        sns.histplot(df[feature].dropna(), kde=True, ax=axes[i], bins=25, color='steelblue')
        axes[i].set_title(feature, fontsize=9)
        axes[i].set_xlabel('')
        axes[i].tick_params(axis='x', rotation=45, labelsize=8)

for i in range(len(numeric_cols), len(axes)):
    axes[i].set_visible(False)

plt.suptitle('Распределение всех числовых признаков', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('analysis_plots/6_all_distributions.png', dpi=150, bbox_inches='tight')
plt.show()

# ============================================
# 7. СТАТИСТИЧЕСКИЕ ТЕСТЫ
# ============================================

print("\n" + "=" * 80)
print("7. СТАТИСТИЧЕСКИЕ ТЕСТЫ")
print("=" * 80)

print("\nТест Шапиро-Уилка на нормальность распределения:")
for feature in plot_features[:5]:
    if feature in df.columns:
        data = df[feature].dropna()
        if len(data) > 3 and len(data) < 5000:
            stat, p_value = stats.shapiro(data)
            normal = "нормальное" if p_value > 0.05 else "НЕ нормальное"
            print(f"  {feature:20s}: p-value = {p_value:.4f} -> {normal}")

if 'пол' in df.columns and 'КПУ' in df.columns:
    male_kpu = df[df['пол'] == 1]['КПУ'].dropna()
    female_kpu = df[df['пол'] == 0]['КПУ'].dropna()
    if len(male_kpu) > 0 and len(female_kpu) > 0:
        t_stat, p_val = stats.ttest_ind(male_kpu, female_kpu)
        print(f"\nСравнение КПУ по полу (t-test):")
        print(f"  Мужчины: n={len(male_kpu)}, mean={male_kpu.mean():.2f}")
        print(f"  Женщины: n={len(female_kpu)}, mean={female_kpu.mean():.2f}")
        print(f"  p-value = {p_val:.4f} -> {'значимо' if p_val < 0.05 else 'не значимо'}")

# ============================================
# 8. ВЫВОДЫ
# ============================================

print("\n" + "=" * 80)
print("8. ОСНОВНЫЕ ВЫВОДЫ")
print("=" * 80)

print("""
ОБЩАЯ ХАРАКТЕРИСТИКА ДАННЫХ:
   - Данные содержат информацию о пациентах стоматологической клиники
   - Включают клинические, лабораторные и антропометрические показатели
   - Содержат факторы риска стоматологических заболеваний

КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ:
   - КПУ (интенсивность кариеса)
   - Содержание фтора в моче (показатель поступления фтора в организм)
   - Содержание йода в моче
   - pH показатели (слюна, моча, вода, чай)

РЕКОМЕНДАЦИИ ПО ДАЛЬНЕЙШЕМУ АНАЛИЗУ:
   1. Провести множественный регрессионный анализ для выявления факторов, 
      влияющих на КПУ
   2. Выполнить кластерный анализ для выделения групп пациентов со схожими 
      характеристиками
   3. Исследовать взаимосвязь между потреблением фтора и состоянием зубов
   4. Учесть выбросы при построении прогностических моделей
""")

stats_df.to_csv('analysis_plots/descriptive_statistics.csv')
outliers_df.to_csv('analysis_plots/outliers_analysis.csv')
print(f"\nСтатистика сохранена в папку 'analysis_plots/'")
print(f"Графики сохранены в папку 'analysis_plots/'")

# ============================================
# 9. СВОДНАЯ ТАБЛИЦА
# ============================================

print("\n" + "=" * 80)
print("9. СВОДНАЯ ТАБЛИЦА ПО КАТЕГОРИЯМ ПРИЗНАКОВ")
print("=" * 80)

categories = {
    'pH показатели': ['pH_слюны', 'pH_слюны_2', 'pH_мочи_утро', 'pH_мочи_день',
                      'pH_мочи_вечер', 'pH_мочи_средняя', 'pH_вода', 'pH_чай'],
    'Антропометрия': ['возраст', 'рост', 'вес', 'энергозатраты'],
    'Стоматология': ['КПУ'],
    'Фтор (продукты, вода)': ['фтор_продукты', 'фтор_вода', 'фтор_чай', 'фтор_моча_кг'],
    'Фтор (соотношения)': ['фтор_белок', 'фтор_жиры', 'фтор_кальций'],
    'Питание': ['белок_продукты', 'жиры_продукты', 'кальций_продукты'],
    'Факторы риска': ['рефлюкс', 'курение_алкоголь', 'пародонтит', 'кариес',
                      'риск_кариеса', 'бруксизм', 'эндокринные', 'пол'],
    'Лабораторные': ['йод_моча', 'фтор_воздух', 'гидрофторид_ПДК']
}

summary_categories = []
for cat, features in categories.items():
    existing = [f for f in features if f in df.columns]
    if existing:
        summary_categories.append({
            'Категория': cat,
            'Кол-во признаков': len(existing)
        })

summary_df = pd.DataFrame(summary_categories)
print(summary_df.to_string(index=False))

print("\n" + "=" * 80)
print("АНАЛИЗ ЗАВЕРШЕН!")
print("=" * 80)
# ============================================
# 10. РЕГРЕССИОННЫЙ АНАЛИЗ ДЛЯ ВЫЯВЛЕНИЯ ПРЕДИКТОРОВ КПУ
# ============================================

print("\n" + "=" * 80)
print("10. РЕГРЕССИОННЫЙ АНАЛИЗ: ПРЕДИКТОРЫ КПУ")
print("=" * 80)

from sklearn.linear_model import LinearRegression, LassoCV, RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_squared_error, r2_score
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Подготовка данных
if 'КПУ' in df.columns:
    # Убираем строки с пропусками в КПУ
    data_for_regression = df.dropna(subset=['КПУ'])

    # Выбираем потенциальные предикторы (исключаем КПУ и явно связанные признаки)
    exclude_cols = ['КПУ', 'кариес', 'риск_кариеса']  # исключаем коллинеарные
    potential_predictors = [col for col in numeric_cols if col not in exclude_cols]

    # Дополнительно исключаем признаки с низкой вариативностью
    predictors = []
    for col in potential_predictors:
        if data_for_regression[col].std() > 0.01:  # есть вариативность
            predictors.append(col)

    X = data_for_regression[predictors]
    y = data_for_regression['КПУ']

    print(f"\nИсходное количество потенциальных предикторов: {len(predictors)}")

    # 10.1 Корреляции с КПУ (ранжирование)
    print("\n" + "-" * 40)
    print("10.1 РАНЖИРОВАНИЕ ПРЕДИКТОРОВ ПО КОРРЕЛЯЦИИ С КПУ")
    print("-" * 40)

    correlations = []
    for col in predictors:
        corr_val = data_for_regression[col].corr(data_for_regression['КПУ'])
        correlations.append({'Признак': col, 'Корреляция с КПУ': corr_val})

    corr_df = pd.DataFrame(correlations).sort_values('Корреляция с КПУ', key=abs, ascending=False)
    print(corr_df.head(15).to_string(index=False))

    # 10.2 Множественная линейная регрессия (шаг 1: все признаки)
    print("\n" + "-" * 40)
    print("10.2 МНОЖЕСТВЕННАЯ ЛИНЕЙНАЯ РЕГРЕССИЯ (все признаки)")
    print("-" * 40)

    # Стандартизация
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=X.columns)

    # Регрессия с OLS (statsmodels для получения p-values)
    X_with_const = sm.add_constant(X_scaled)
    model_ols = sm.OLS(y, X_with_const).fit()

    print("\nРезультаты OLS регрессии (первые 20 признаков):")
    ols_results = pd.DataFrame({
        'Признак': model_ols.params.index,
        'Коэффициент': model_ols.params.values,
        'p-value': model_ols.pvalues.values,
        'Значимо': ['✅' if p < 0.05 else '❌' for p in model_ols.pvalues.values]
    })
    # Сортируем по абсолютному значению коэффициента
    ols_results['abs_coef'] = ols_results['Коэффициент'].abs()
    ols_results = ols_results.sort_values('abs_coef', ascending=False)
    print(ols_results[ols_results['Признак'] != 'const'].head(20).to_string(index=False))

    # 10.3 Отбор значимых предикторов (p-value < 0.05)
    print("\n" + "-" * 40)
    print("10.3 ЗНАЧИМЫЕ ПРЕДИКТОРЫ (p-value < 0.05)")
    print("-" * 40)

    significant = ols_results[(ols_results['p-value'] < 0.05) & (ols_results['Признак'] != 'const')]
    if len(significant) > 0:
        print(significant[['Признак', 'Коэффициент', 'p-value']].to_string(index=False))
    else:
        print("Нет значимых предикторов при p<0.05")

    # 10.4 LASSO регрессия (автоматический отбор признаков)
    print("\n" + "-" * 40)
    print("10.4 LASSO РЕГРЕССИЯ (отбор признаков)")
    print("-" * 40)

    # Подбор alpha по кросс-валидации
    lasso = LassoCV(cv=5, random_state=42, alphas=np.logspace(-4, 1, 50))
    lasso.fit(X_scaled, y)

    # Получаем ненулевые коэффициенты
    lasso_coefs = pd.DataFrame({
        'Признак': X.columns,
        'Коэффициент_LASSO': lasso.coef_
    })
    lasso_coefs = lasso_coefs[lasso_coefs['Коэффициент_LASSO'].abs() > 0.01]
    lasso_coefs = lasso_coefs.sort_values('Коэффициент_LASSO', key=abs, ascending=False)

    print(f"\nОптимальный alpha LASSO: {lasso.alpha_:.4f}")
    print(f"R² на кросс-валидации: {lasso.score(X_scaled, y):.4f}")
    print(f"\nОтобранные LASSO признаки ({len(lasso_coefs)}):")
    print(lasso_coefs.to_string(index=False))

    # 10.5 Ridge регрессия (для сравнения)
    print("\n" + "-" * 40)
    print("10.5 RIDGE РЕГРЕССИЯ")
    print("-" * 40)

    ridge = RidgeCV(alphas=np.logspace(-3, 3, 50), cv=5)
    ridge.fit(X_scaled, y)

    ridge_coefs = pd.DataFrame({
        'Признак': X.columns,
        'Коэффициент_Ridge': ridge.coef_
    })
    ridge_coefs = ridge_coefs.sort_values('Коэффициент_Ridge', key=abs, ascending=False)

    print(f"\nОптимальный alpha Ridge: {ridge.alpha_:.4f}")
    print(f"R²: {ridge.score(X_scaled, y):.4f}")
    print(f"\nТоп-15 коэффициентов Ridge:")
    print(ridge_coefs.head(15).to_string(index=False))

    # 10.6 Финальная модель (только топ-5 предикторов)
    print("\n" + "-" * 40)
    print("10.6 ФИНАЛЬНАЯ МОДЕЛЬ (топ-5 предикторов по LASSO)")
    print("-" * 40)

    if len(lasso_coefs) > 0:
        top_predictors = lasso_coefs.head(5)['Признак'].tolist()
        X_final = data_for_regression[top_predictors]
        X_final_scaled = scaler.fit_transform(X_final)
        X_final_with_const = sm.add_constant(X_final_scaled)

        final_model = sm.OLS(y, X_final_with_const).fit()

        print("\nФинальная регрессионная модель:")
        final_results = pd.DataFrame({
            'Признак': final_model.params.index,
            'Коэффициент': final_model.params.values,
            'p-value': final_model.pvalues.values,
            '95% CI нижн': final_model.conf_int()[0],
            '95% CI верхн': final_model.conf_int()[1]
        })
        print(final_results.round(4).to_string(index=False))

        print(f"\nМетрики финальной модели:")
        print(f"  R² = {final_model.rsquared:.4f}")
        print(f"  Adjusted R² = {final_model.rsquared_adj:.4f}")
        print(f"  F-statistic = {final_model.fvalue:.2f}")
        print(f"  F-test p-value = {final_model.f_pvalue:.4f}")
        print(f"  AIC = {final_model.aic:.2f}")
        print(f"  BIC = {final_model.bic:.2f}")

        # 10.7 Проверка мультиколлинеарности
        print("\n" + "-" * 40)
        print("10.7 ПРОВЕРКА МУЛЬТИКОЛЛИНЕАРНОСТИ (VIF)")
        print("-" * 40)

        vif_data = pd.DataFrame()
        vif_data['Признак'] = X_final.columns
        vif_data['VIF'] = [variance_inflation_factor(X_final.values, i) for i in range(X_final.shape[1])]
        print(vif_data.to_string(index=False))
        print("Примечание: VIF > 5-10 указывает на мультиколлинеарность")

        # 10.8 Визуализация результатов
        print("\n" + "-" * 40)
        print("10.8 ВИЗУАЛИЗАЦИЯ РЕЗУЛЬТАТОВ")
        print("-" * 40)

        # График: Predicted vs Actual
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Predicted vs Actual
        y_pred = final_model.predict(X_final_with_const)
        axes[0, 0].scatter(y, y_pred, alpha=0.6, color='steelblue')
        axes[0, 0].plot([y.min(), y.max()], [y.min(), y.max()], 'r--', lw=2)
        axes[0, 0].set_xlabel('Фактический КПУ')
        axes[0, 0].set_ylabel('Предсказанный КПУ')
        axes[0, 0].set_title(f'Predicted vs Actual (R² = {final_model.rsquared:.3f})')

        # Коэффициенты финальной модели
        coef_plot = final_results[final_results['Признак'] != 'const'].copy()
        colors = ['green' if c > 0 else 'red' for c in coef_plot['Коэффициент']]
        axes[0, 1].barh(coef_plot['Признак'], coef_plot['Коэффициент'], color=colors)
        axes[0, 1].axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        axes[0, 1].set_xlabel('Коэффициент')
        axes[0, 1].set_title('Влияние предикторов на КПУ')

        # Остатки
        residuals = y - y_pred
        axes[1, 0].scatter(y_pred, residuals, alpha=0.6, color='steelblue')
        axes[1, 0].axhline(y=0, color='red', linestyle='--')
        axes[1, 0].set_xlabel('Предсказанный КПУ')
        axes[1, 0].set_ylabel('Остатки')
        axes[1, 0].set_title('График остатков')

        # QQ-plot для остатков
        stats.probplot(residuals, dist="norm", plot=axes[1, 1])
        axes[1, 1].set_title('QQ-plot остатков')

        plt.tight_layout()
        plt.savefig('analysis_plots/7_regression_results.png', dpi=150, bbox_inches='tight')
        plt.show()

        # 10.9 Выводы
        print("\n" + "=" * 80)
        print("ВЫВОДЫ ПО РЕГРЕССИОННОМУ АНАЛИЗУ")
        print("=" * 80)

        print("\n📌 ОСНОВНЫЕ ПРЕДИКТОРЫ КПУ (в порядке значимости):")
        for i, row in coef_plot.sort_values('Коэффициент', key=abs, ascending=False).iterrows():
            effect = "положительно" if row['Коэффициент'] > 0 else "отрицательно"
            print(f"   {row['Признак']}: {effect} влияет на КПУ (коэф = {row['Коэффициент']:.3f})")

        print(f"\n📌 КАЧЕСТВО МОДЕЛИ:")
        print(f"   Модель объясняет {final_model.rsquared:.1%} вариации КПУ")
        print(f"   Скорректированный R² = {final_model.rsquared_adj:.1%}")

        if final_model.rsquared < 0.3:
            print("   ⚠️ Низкая предсказательная способность. Возможно, нужны дополнительные признаки.")
        elif final_model.rsquared < 0.6:
            print("   ✅ Средняя предсказательная способность. Модель полезна для анализа.")
        else:
            print("   ✅✅ Высокая предсказательная способность. Модель отлично описывает данные.")

        # Сохраняем результаты
        final_results.to_csv('analysis_plots/regression_coefficients.csv', index=False)
        if len(significant) > 0:
            significant.to_csv('analysis_plots/significant_predictors.csv', index=False)

        print(f"\n✅ Результаты регрессии сохранены в папку 'analysis_plots/'")

else:
    print("⚠️ Признак 'КПУ' не найден в данных. Регрессионный анализ невозможен.")
