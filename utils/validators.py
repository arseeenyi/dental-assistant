"""Валидация входных данных"""

def validate_age(age):
    if age is None:
        return None, "Возраст обязателен"
    try:
        age = float(age)
        if 0 <= age <= 120:
            return age, None
        else:
            return None, "Возраст должен быть от 0 до 120 лет"
    except ValueError:
        return None, "Введите корректное число"

def validate_height(height):
    if height is None:
        return None, "Рост обязателен"
    try:
        height = float(height)
        if 50 <= height <= 250:
            return height, None
        else:
            return None, "Рост должен быть от 50 до 250 см"
    except ValueError:
        return None, "Введите корректное число"

def validate_weight(weight):
    if weight is None:
        return None, "Вес обязателен"
    try:
        weight = float(weight)
        if 10 <= weight <= 300:
            return weight, None
        else:
            return None, "Вес должен быть от 10 до 300 кг"
    except ValueError:
        return None, "Введите корректное число"

def validate_ph(value, name="pH"):
    if value is None:
        return None, f"{name} обязателен"
    try:
        value = float(value)
        if 0 <= value <= 14:
            return value, None
        else:
            return None, f"{name} должен быть от 0 до 14"
    except ValueError:
        return None, f"Введите корректное число для {name}"

def validate_fluorine(value, name="Фтор"):
    if value is None:
        return None, f"{name} обязателен"
    try:
        value = float(value)
        if 0 <= value <= 10:
            return value, None
        else:
            return None, f"{name} должен быть от 0 до 10"
    except ValueError:
        return None, f"Введите корректное число для {name}"