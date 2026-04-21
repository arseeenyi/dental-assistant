"""
Генерация клинических рекомендаций
"""


def generate_recommendations(results):
    recommendations = []

    kpu = results.get('КПУ', 0)
    if kpu > 10:
        recommendations.append(
            {'text': 'Critically high DMFT index. Urgent dental care, professional hygiene required.'})
    elif kpu > 7:
        recommendations.append(
            {'text': 'High DMFT index. Dental care, fluoride products, hygiene control recommended.'})
    elif kpu > 3:
        recommendations.append({'text': 'Medium DMFT index. Preventive examination every 6 months.'})
    else:
        recommendations.append({'text': 'Low DMFT index. Preventive examination once a year.'})

    paro = results.get('пародонтит', {})
    if paro.get('risk', False):
        recommendations.append({'text': 'Periodontitis risk detected. Professional teeth cleaning recommended.'})

    reflux = results.get('рефлюкс', {})
    if reflux.get('risk', False):
        recommendations.append({'text': 'Reflux risk detected. Gastroenterology consultation recommended.'})

    fluorine = results.get('фтор_моча_кг', 0)
    if fluorine < 0.3:
        recommendations.append({'text': 'Low fluorine level. Use fluoride-containing toothpaste.'})
    elif fluorine > 1.5:
        recommendations.append({'text': 'High fluorine level. Monitor fluorine intake.'})

    return recommendations