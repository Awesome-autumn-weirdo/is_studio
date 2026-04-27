from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Получить значение из словаря по ключу"""
    if dictionary is None:
        return None
    return dictionary.get(key)


@register.filter
def get_by_student_id(stats_list, student_id):
    """Найти статистику студента по ID"""
    for item in stats_list:
        if item['student'].id == student_id:
            return item
    return {'present': 0, 'absent': 0, 'late': 0, 'excused': 0}