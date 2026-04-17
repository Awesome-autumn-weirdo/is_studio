from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    """Доступ только для администраторов"""
    def check_admin(user):
        return user.is_authenticated and (
            user.is_superuser or 
            user.groups.filter(name='Администраторы').exists()
        )
    return user_passes_test(check_admin, login_url='login')(view_func)


def teacher_required(view_func):
    """Доступ только для преподавателей"""
    def check_teacher(user):
        return user.is_authenticated and user.groups.filter(name='Преподаватели').exists()
    return user_passes_test(check_teacher, login_url='login')(view_func)


def student_required(view_func):
    """Доступ только для студентов"""
    def check_student(user):
        return user.is_authenticated and user.groups.filter(name='Студенты').exists()
    return user_passes_test(check_student, login_url='login')(view_func)


def manager_required(view_func):
    """Доступ для менеджеров и администраторов"""
    def check_manager(user):
        return user.is_authenticated and (
            user.groups.filter(name='Менеджеры').exists() or
            user.groups.filter(name='Администраторы').exists() or
            user.is_superuser
        )
    return user_passes_test(check_manager, login_url='login')(view_func)