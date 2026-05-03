"""
Подсказки для полей ввода
"""

HINTS = {
    # Личные данные
    'age': {
        'label': "📅 Возраст",
        'tooltip': "Полных лет на момент осмотра. Норма: 18-65 лет.",
        'norm': "Взрослый пациент: 18-65 лет",
        'warning_low': "Молодой возраст (<18 лет)",
        'warning_high': "Пожилой возраст (>65 лет)"
    },
    'height': {
        'label': "📏 Рост",
        'tooltip': "Рост в сантиметрах. Норма: 150-190 см.",
        'norm': "Средний рост: 150-190 см",
        'warning_low': "Низкий рост (<150 см)",
        'warning_high': "Высокий рост (>190 см)"
    },
    'weight': {
        'label': "⚖️ Вес",
        'tooltip': "Вес в килограммах. Норма зависит от роста и возраста.",
        'norm': "Рекомендуемый диапазон: 50-100 кг",
        'warning_low': "Низкий вес (<50 кг)",
        'warning_high': "Высокий вес (>100 кг)"
    },
    'gender': {
        'label': "🚻 Пол",
        'tooltip': "Биологический пол пациента. Влияет на некоторые показатели.",
        'norm': "Мужской или Женский"
    },

    # Лабораторные показатели
    'ph_saliva': {
        'label': "💧 pH слюны",
        'tooltip': "Кислотность слюны. Норма: 6.5-7.5. Низкий pH → риск кариеса.",
        'norm': "Норма: 6.5-7.5",
        'warning_low': "Кислая среда (<6.5) → риск кариеса ⚠️",
        'warning_high': "Щелочная среда (>7.5) → редко"
    },
    'ph_water': {
        'label': "🚰 pH воды",
        'tooltip': "Кислотность питьевой воды. Норма: 6.5-8.5 (СанПиН).",
        'norm': "Норма по СанПиН: 6.5-8.5",
        'warning_low': "Кислая вода (<6.5)",
        'warning_high': "Щелочная вода (>8.5)"
    },
    'ph_tea': {
        'label': "🍵 pH чая",
        'tooltip': "Кислотность чая. Обычно 5.5-7.0. Крепкий чай более кислый.",
        'norm': "Обычный чай: 5.5-7.0",
        'warning_low': "Очень кислый чай (<5.0)",
        'warning_high': "Слабый чай (>7.0)"
    },

    # Фтор
    'fluorine_water': {
        'label': "💧 Фтор в воде",
        'tooltip': "Концентрация фтора в питьевой воде. ПДК: 1.5 мг/л.",
        'norm': "Норма: 0.5-1.5 мг/л",
        'warning_low': "Дефицит фтора (<0.5 мг/л) → риск кариеса ⚠️",
        'warning_high': "Избыток фтора (>1.5 мг/л) → флюороз ⚠️"
    },
    'fluorine_products': {
        'label': "🥗 Фтор в продуктах",
        'tooltip': "Поступление фтора с пищей в день. Норма: 2-4 мг.",
        'norm': "Рекомендуемое суточное потребление: 2-4 мг",
        'warning_low': "Недостаточное потребление (<2 мг)",
        'warning_high': "Избыточное потребление (>4 мг)"
    },
    'fluorine_tea': {
        'label': "🍵 Фтор в чае",
        'tooltip': "Содержание фтора в чае. Заварка влияет на концентрацию.",
        'norm': "Обычный чай: 0.3-1.0 мг",
        'warning_high': "Высокое содержание (>1.0 мг)"
    },

    # Факторы риска
    'smoking': {
        'label': "🚬 Курение/алкоголь",
        'tooltip': "Наличие вредных привычек. Повышает риск заболеваний пародонта.",
        'norm': "Отсутствие вредных привычек — оптимально",
        'warning': "Вредные привычки повышают риск пародонтита ⚠️"
    },
    'bruxism': {
        'label': "😬 Бруксизм",
        'tooltip': "Скрежетание зубами во сне. Приводит к стираемости эмали.",
        'norm': "Отсутствие бруксизма — норма",
        'warning': "Бруксизм → риск стираемости эмали ⚠️"
    },
    'endocrine': {
        'label': "🦋 Эндокринные нарушения",
        'tooltip': "Заболевания щитовидной железы, диабет и др. Влияют на состояние полости рта.",
        'norm': "Нет эндокринных нарушений",
        'warning': "Эндокринные нарушения → риск осложнений ⚠️"
    }
}


def get_hint(field_name):
    """Получить подсказку для поля"""
    return HINTS.get(field_name, {})


def get_tooltip(field_name):
    """Получить tooltip для поля"""
    hint = get_hint(field_name)
    return hint.get('tooltip', '')


def get_norm_text(field_name, value=None):
    """Получить текст нормы и предупреждение при отклонении"""
    hint = get_hint(field_name)
    norm_text = hint.get('norm', '')

    # Проверка отклонений (если передано значение)
    if value is not None:
        if field_name == 'age':
            if value < 18:
                return f"⚠️ {hint.get('warning_low', '')}"
            elif value > 65:
                return f"⚠️ {hint.get('warning_high', '')}"
        elif field_name == 'ph_saliva':
            if value < 6.5:
                return f"⚠️ {hint.get('warning_low', '')}"
            elif value > 7.5:
                return f"⚠️ {hint.get('warning_high', '')}"
        elif field_name == 'fluorine_water':
            if value < 0.5:
                return f"⚠️ {hint.get('warning_low', '')}"
            elif value > 1.5:
                return f"⚠️ {hint.get('warning_high', '')}"
        elif field_name in ['smoking', 'bruxism', 'endocrine']:
            if value == "Да":
                return f"⚠️ {hint.get('warning', '')}"

    return norm_text