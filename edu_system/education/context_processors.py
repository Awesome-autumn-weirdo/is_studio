def user_groups(request):
    """Добавляет список групп пользователя в контекст"""
    if request.user.is_authenticated:
        groups = list(request.user.groups.values_list('name', flat=True))
        return {'user_groups': groups}
    return {'user_groups': []}

def user_permissions(request):
    """Добавляет информацию о правах пользователя в контекст"""
    context = {
        'user_groups': [],
        'is_admin': False,
        'is_teacher': False,
        'is_student': False,
        'is_marketer': False,
    }
    
    if request.user.is_authenticated:
        groups = list(request.user.groups.values_list('name', flat=True))
        context['user_groups'] = groups
        context['is_admin'] = request.user.is_superuser or 'Администраторы' in groups
        context['is_teacher'] = 'Преподаватели' in groups
        context['is_student'] = 'Студенты' in groups
        context['is_marketer'] = 'Маркетологи' in groups
    
    return context