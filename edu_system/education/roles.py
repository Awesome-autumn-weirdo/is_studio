from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import (
    Course, Category, Teacher, Student, Group as EduGroup, 
    Enrollment, Schedule, Attendance, Performance, Review
)

def create_roles_and_permissions():
    """Создание ролей и назначение прав согласно таблице ролей"""
    
    # Создаем группы (роли)
    admin_group, _ = Group.objects.get_or_create(name='Администраторы')
    teacher_group, _ = Group.objects.get_or_create(name='Преподаватели')
    student_group, _ = Group.objects.get_or_create(name='Студенты')
    marketer_group, _ = Group.objects.get_or_create(name='Маркетологи')
    
    # Получаем ContentType для всех моделей
    course_ct = ContentType.objects.get_for_model(Course)
    category_ct = ContentType.objects.get_for_model(Category)
    teacher_ct = ContentType.objects.get_for_model(Teacher)
    student_ct = ContentType.objects.get_for_model(Student)
    group_ct = ContentType.objects.get_for_model(EduGroup)
    enrollment_ct = ContentType.objects.get_for_model(Enrollment)
    schedule_ct = ContentType.objects.get_for_model(Schedule)
    attendance_ct = ContentType.objects.get_for_model(Attendance)
    performance_ct = ContentType.objects.get_for_model(Performance)
    review_ct = ContentType.objects.get_for_model(Review)
    
    # ===== АДМИНИСТРАТОР =====
    # Полный доступ ко всему
    all_permissions = Permission.objects.all()
    admin_group.permissions.set(all_permissions)
    
    # ===== ПРЕПОДАВАТЕЛЬ =====
    teacher_permissions = [
        # Просмотр информации о курсах и группах
        Permission.objects.get(codename='view_course', content_type=course_ct),
        Permission.objects.get(codename='view_group', content_type=group_ct),
        Permission.objects.get(codename='view_student', content_type=student_ct),
        Permission.objects.get(codename='view_enrollment', content_type=enrollment_ct),
        
        # Просмотр и редактирование своего расписания
        Permission.objects.get(codename='view_schedule', content_type=schedule_ct),
        
        # Работа с посещаемостью
        Permission.objects.get(codename='view_attendance', content_type=attendance_ct),
        Permission.objects.get(codename='add_attendance', content_type=attendance_ct),
        Permission.objects.get(codename='change_attendance', content_type=attendance_ct),
        
        # Работа с успеваемостью
        Permission.objects.get(codename='view_performance', content_type=performance_ct),
        Permission.objects.get(codename='add_performance', content_type=performance_ct),
        Permission.objects.get(codename='change_performance', content_type=performance_ct),
        
        # Редактирование своих данных
        Permission.objects.get(codename='change_teacher', content_type=teacher_ct),
    ]
    teacher_group.permissions.set(teacher_permissions)
    
    # ===== СТУДЕНТ =====
    student_permissions = [
        # Просмотр курсов, категорий, преподавателей
        Permission.objects.get(codename='view_course', content_type=course_ct),
        Permission.objects.get(codename='view_category', content_type=category_ct),
        Permission.objects.get(codename='view_teacher', content_type=teacher_ct),
        Permission.objects.get(codename='view_group', content_type=group_ct),
        
        # Просмотр своего расписания
        Permission.objects.get(codename='view_schedule', content_type=schedule_ct),
        
        # Просмотр своей успеваемости и посещаемости
        Permission.objects.get(codename='view_attendance', content_type=attendance_ct),
        Permission.objects.get(codename='view_performance', content_type=performance_ct),
        
        # Редактирование своих данных
        Permission.objects.get(codename='change_student', content_type=student_ct),
        
        # Создание и редактирование своих отзывов
        Permission.objects.get(codename='add_review', content_type=review_ct),
        Permission.objects.get(codename='change_review', content_type=review_ct),
    ]
    student_group.permissions.set(student_permissions)
    
    # ===== МАРКЕТОЛОГ =====
    marketer_permissions = [
        # Просмотр курсов и категорий
        Permission.objects.get(codename='view_course', content_type=course_ct),
        Permission.objects.get(codename='view_category', content_type=category_ct),
        
        # Управление курсами (для размещения рекламных материалов)
        Permission.objects.get(codename='change_course', content_type=course_ct),
        
        # Просмотр и управление отзывами
        Permission.objects.get(codename='view_review', content_type=review_ct),
        Permission.objects.get(codename='add_review', content_type=review_ct),
        Permission.objects.get(codename='change_review', content_type=review_ct),
        Permission.objects.get(codename='delete_review', content_type=review_ct),
        
        # Просмотр статистики (студенты, записи)
        Permission.objects.get(codename='view_student', content_type=student_ct),
        Permission.objects.get(codename='view_enrollment', content_type=enrollment_ct),
    ]
    marketer_group.permissions.set(marketer_permissions)
    

def assign_user_to_role(user, role_name):
    """Назначить пользователю роль"""
    try:
        group = Group.objects.get(name=role_name)
        user.groups.clear()  # Удаляем старые группы
        user.groups.add(group)
        user.save()
        return True
    except Group.DoesNotExist:
        return False


def get_user_role(user):
    """Получить роль пользователя"""
    if user.is_superuser:
        return 'Администратор'
    
    groups = user.groups.all()
    if groups.exists():
        return groups.first().name
    
    return 'Без роли'