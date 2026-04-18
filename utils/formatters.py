"""Форматирование результатов для отображения"""

def format_kpu(value):
    if value < 3:
        return f"🟢 {value:.1f} (низкий)"
    elif value < 7:
        return f"🟡 {value:.1f} (средний)"
    else:
        return f"🔴 {value:.1f} (высокий)"

def get_kpu_color(value):
    if value < 3:
        return "green"
    elif value < 7:
        return "orange"
    else:
        return "red"

def format_risk(percent, is_risk):
    if is_risk:
        return f"🔴 Есть риск ({percent:.1f}%)"
    else:
        return f"🟢 Нет риска ({100-percent:.1f}%)"

def format_fluorine(value):
    if value < 0.3:
        return f"🟡 {value:.2f} мкг/кг (низкий)"
    elif value < 1.5:
        return f"🟢 {value:.2f} мкг/кг (оптимальный)"
    else:
        return f"🔴 {value:.2f} мкг/кг (высокий)"

def get_fluorine_color(value):
    if value < 0.3:
        return "orange"
    elif value < 1.5:
        return "green"
    else:
        return "red"