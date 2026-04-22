"""
СТОМАТОЛОГИЧЕСКИЙ ПОМОЩНИК
Страница "О проекте" - для конференции и презентации
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Настройка страницы
st.set_page_config(
    page_title="О проекте | Стоматологический помощник",
    page_icon="🦷",
    layout="wide"
)

# Кастомные стили для этой страницы
st.markdown("""
<style>
    /* Заголовок страницы */
    .about-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .about-header h1 {
        font-size: 2.5rem;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .about-header p {
        font-size: 1.1rem;
        color: #7f8c8d;
    }

    /* Карточки */
    .feature-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        height: 100%;
        transition: transform 0.3s ease;
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
    .feature-card h3 {
        margin: 0.5rem 0;
        font-size: 1.3rem;
    }
    .feature-card p {
        margin: 0;
        opacity: 0.9;
        font-size: 0.9rem;
    }

    /* Метрики */
    .metric-box {
        background-color: #f8f9fa;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #e0e0e0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        color: #7f8c8d;
        font-size: 0.85rem;
    }

    /* Прогресс-бар для метрик */
    .progress-bar-container {
        background-color: #ecf0f1;
        border-radius: 10px;
        height: 10px;
        margin: 10px 0;
    }
    .progress-bar {
        background: linear-gradient(90deg, #27ae60, #2ecc71);
        border-radius: 10px;
        height: 100%;
        width: 0%;
    }

    /* Технологии */
    .tech-badge {
        display: inline-block;
        background-color: #e8f4fd;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.8rem;
        color: #2980b9;
    }

    /* Команда */
    .team-card {
        text-align: center;
        padding: 1rem;
    }
    .team-avatar {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .team-name {
        font-weight: bold;
        font-size: 1.1rem;
    }
    .team-role {
        color: #7f8c8d;
        font-size: 0.85rem;
    }

    /* Разделитель */
    .section-divider {
        margin: 2rem 0;
        border-top: 2px solid #e0e0e0;
    }

    /* Ссылки */
    .link-button {
        display: inline-block;
        background-color: #2c3e50;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        text-decoration: none;
        margin: 0.2rem;
        font-size: 0.85rem;
    }
    .link-button:hover {
        background-color: #34495e;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# ЗАГОЛОВОК
# ============================================

st.markdown("""
<div class="about-header">
    <h1>🦷 Стоматологический помощник</h1>
    <p>AI-Powered Clinical Decision Support System</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# ОСНОВНЫЕ ФУНКЦИИ (4 карточки в ряд)
# ============================================

st.markdown("### 🎯 Что умеет приложение")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size: 2rem;">🦷</div>
        <h3>КПУ</h3>
        <p>Прогнозирование индекса кариеса</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size: 2rem;">🦷</div>
        <h3>Пародонтит</h3>
        <p>Оценка риска заболевания</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size: 2rem;">🔥</div>
        <h3>Рефлюкс</h3>
        <p>Выявление факторов эрозии эмали</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="feature-card">
        <div style="font-size: 2rem;">💧</div>
        <h3>Фтор в моче</h3>
        <p>Контроль уровня фтора</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ============================================
# МЕТРИКИ МОДЕЛЕЙ (с прогресс-барами)
# ============================================

st.markdown("### 📊 Качество моделей")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Регрессионные модели")

    # КПУ
    st.markdown("**КПУ (Gradient Boosting)**")
    st.markdown('<div class="progress-bar-container"><div class="progress-bar" style="width: 93%;"></div></div>',
                unsafe_allow_html=True)
    st.caption("R² = 0.93 | MAE = 0.70")

    # Фтор в моче
    st.markdown("**Фтор в моче (Ridge)**")
    st.markdown(
        '<div class="progress-bar-container"><div class="progress-bar" style="width: 70%; background: linear-gradient(90deg, #f39c12, #e67e22);"></div></div>',
        unsafe_allow_html=True)
    st.caption("R² = 0.70 | MAE = 0.005")

with col2:
    st.markdown("#### Классификационные модели")

    # Пародонтит
    st.markdown("**Пародонтит (Random Forest)**")
    st.markdown(
        '<div class="progress-bar-container"><div class="progress-bar" style="width: 100%; background: linear-gradient(90deg, #27ae60, #2ecc71);"></div></div>',
        unsafe_allow_html=True)
    st.caption("AUC = 1.00 | F1 = 0.90 | Accuracy = 95%")

    # Рефлюкс
    st.markdown("**Рефлюкс (Gradient Boosting)**")
    st.markdown(
        '<div class="progress-bar-container"><div class="progress-bar" style="width: 99%; background: linear-gradient(90deg, #27ae60, #2ecc71);"></div></div>',
        unsafe_allow_html=True)
    st.caption("AUC = 0.99 | F1 = 0.99 | Accuracy = 99%")

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ============================================
# ТЕХНОЛОГИИ
# ============================================

st.markdown("### 🤖 Технологический стек")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-box">
        <div style="font-size: 2rem;">🐍</div>
        <div class="metric-value">Python</div>
        <div class="metric-label">Основной язык</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-box">
        <div style="font-size: 2rem;">📊</div>
        <div class="metric-value">Streamlit</div>
        <div class="metric-label">Веб-фреймворк</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-box">
        <div style="font-size: 2rem;">🤖</div>
        <div class="metric-value">scikit-learn</div>
        <div class="metric-label">ML библиотека</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-top: 1rem;">
    <span class="tech-badge">Gradient Boosting</span>
    <span class="tech-badge">Random Forest</span>
    <span class="tech-badge">Ridge Regression</span>
    <span class="tech-badge">Pandas</span>
    <span class="tech-badge">NumPy</span>
    <span class="tech-badge">Matplotlib</span>
    <span class="tech-badge">ReportLab</span>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ============================================
# ДАННЫЕ
# ============================================

st.markdown("### 📁 Данные для обучения")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("👥 Пациентов", ">300", delta="реальных случаев")
with col2:
    st.metric("📊 Признаков", "53", delta="клинических параметров")
with col3:
    st.metric("🦷 Целевых показателей", "4", delta="для прогнозирования")

st.caption("Данные предоставлены стоматологической клиникой (анонимизированы)")

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ============================================
# КОМАНДА ПРОЕКТА (ОБНОВЛЕНО)
# ============================================

st.markdown("### 👨‍🔬 Команда проекта")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="team-card">
        <div class="team-avatar">👨‍💻</div>
        <div class="team-name">Прохоров Арсений Андреевич</div>
        <div class="team-role">Автор проекта</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="team-card">
        <div class="team-avatar">👨‍🏫</div>
        <div class="team-name">Масюк Максим Анатольевич</div>
        <div class="team-role">Научный руководитель</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="team-card">
        <div class="team-avatar">🏥</div>
        <div class="team-name">Клиника "Реновацио"</div>
        <div class="team-role">Клинический партнер</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ============================================
# ССЫЛКИ И КОНТАКТЫ
# ============================================

st.markdown("### 🔗 Полезные ссылки")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div style="background-color: #f8f9fa; border-radius: 10px; padding: 1rem;">
        <strong>📦 GitHub репозиторий</strong><br>
        <code>github.com/arseeenyi/dental-assistant</code>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div style="background-color: #f8f9fa; border-radius: 10px; padding: 1rem;">
        <strong>🌐 Демо приложения</strong><br>
        <code>dental-assistant.streamlit.app</code>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# ПОДВАЛ
# ============================================

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #95a5a6; font-size: 0.8rem; padding: 1rem;">
    <strong>Стоматологический помощник</strong> — версия 1.1<br>
    Разработано для ВКР | {datetime.now().strftime("%Y-%m-%d")}
</div>
""", unsafe_allow_html=True)