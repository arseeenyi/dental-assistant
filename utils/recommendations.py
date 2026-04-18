"""Генерация клинических рекомендаций"""


def generate_recommendations(results):
    recommendations = []

    kpu = results.get('КПУ', 0)
    if kpu > 10:
        recommendations.append({
            'level': 'high',
            'text': 'Критически высокий индекс КПУ. Срочная санация полости рта, профессиональная гигиена.'
        })
    elif kpu > 7:
        recommendations.append({
            'level': 'high',
            'text': 'Высокий индекс КПУ. Рекомендуется санация, фторсодержащие средства, контроль гигиены.'
        })
    elif kpu > 3:
        recommendations.append({
            'level': 'medium',
            'text': 'Средний индекс КПУ. Профилактический осмотр каждые 6 месяцев.'
        })
    else:
        recommendations.append({
            'level': 'low',
            'text': 'Низкий индекс КПУ. Профилактический осмотр раз в год.'
        })

    paro = results.get('пародонтит', {})
    if paro.get('risk', False):
        recommendations.append({
            'level': 'high',
            'text': 'Риск пародонтита. Рекомендуется профессиональная чистка зубов, обучение гигиене.'
        })

    reflux = results.get('рефлюкс', {})
    if reflux.get('risk', False):
        recommendations.append({
            'level': 'medium',
            'text': 'Риск рефлюкса. Рекомендуется консультация гастроэнтеролога.'
        })

    fluorine = results.get('фтор_моча_кг', 0)
    if fluorine < 0.3:
        recommendations.append({
            'level': 'medium',
            'text': 'Низкий уровень фтора. Используйте фторсодержащую зубную пасту.'
        })
    elif fluorine > 1.5:
        recommendations.append({
            'level': 'medium',
            'text': 'Повышенный уровень фтора. Контролируйте потребление фтора.'
        })

    return recommendations