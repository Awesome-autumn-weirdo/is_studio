from django.db import models
from django.contrib.auth.models import User, Group as AuthGroup
from django.urls import reverse

from django.core.validators import FileExtensionValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import sys

from django.dispatch import receiver
from django.db.models.signals import post_save


def validate_image_size(value):
    """Проверка размера файла (максимум 5 МБ)"""
    filesize = value.size
    max_size = 5 * 1024 * 1024  # 5 МБ в байтах
    
    if filesize > max_size:
        raise ValidationError(f'Максимальный размер файла 5 МБ. Ваш файл: {filesize / (1024*1024):.1f} МБ')

class Teacher(models.Model):

    """Преподаватели"""

    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='teacher_profile',
        verbose_name="Пользователь"
    )
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=50, blank=True, verbose_name="Отчество")
    specialization = models.CharField(max_length=100, verbose_name="Специализация")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(max_length=100, blank=True, verbose_name="Email")
    bio = models.TextField(blank=True, verbose_name="Биография")
    photo = models.ImageField(
        upload_to='teachers/%Y/%m/',
        blank=True,
        null=True,
        verbose_name="Фото",
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
            validate_image_size
        ],
        help_text="Поддерживаются форматы: JPG, PNG, GIF. Максимальный размер: 5 МБ"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    class Meta:
        db_table = 'teachers'
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def get_full_name(self):
        """Возвращает полное имя преподавателя"""
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)
    
    def save(self, *args, **kwargs):
        """Синхронизация с User, назначение роли и сжатие фото"""
        
        # Синхронизация данных с User
        if self.user:
            # Копируем данные из Teacher в User (если они заполнены)
            if self.first_name:
                self.user.first_name = self.first_name
            if self.last_name:
                self.user.last_name = self.last_name
            if self.email:
                self.user.email = self.email
            self.user.save()
        else:
            # Если пользователь не указан, но есть email - ищем или создаем
            if self.email:
                user, created = User.objects.get_or_create(
                    username=self.email.split('@')[0],
                    defaults={
                        'email': self.email,
                        'first_name': self.first_name,
                        'last_name': self.last_name,
                    }
                )
                if not created:
                    # Если пользователь уже существовал - обновляем его данные
                    user.first_name = self.first_name
                    user.last_name = self.last_name
                    user.email = self.email
                    user.save()
                self.user = user
        
        # Сжатие и ресайз изображения
        if self.photo:
            img = Image.open(self.photo)
            max_width = 400
            max_height = 400
            
            if img.width > max_width or img.height > max_height:
                output_size = (max_width, max_height)
                img.thumbnail(output_size, Image.Resampling.LANCZOS)
                
                output = BytesIO()
                
                if img.format == 'PNG':
                    img.save(output, format='PNG', optimize=True, quality=85)
                elif img.format == 'GIF':
                    img.save(output, format='GIF', optimize=True)
                else:
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    img.save(output, format='JPEG', optimize=True, quality=85)
                
                output.seek(0)
                self.photo = ContentFile(output.read(), name=self.photo.name)
        
        # Сохраняем преподавателя
        super().save(*args, **kwargs)
        
        # Назначаем роль после сохранения
        if self.user and self.is_active:
            teacher_group, _ = AuthGroup.objects.get_or_create(name='Преподаватели')
            self.user.groups.add(teacher_group)


class Category(models.Model):
    """Категории курсов (иностранные языки, подготовка к ЕГЭ и т.д.)"""
    name = models.CharField(max_length=100, verbose_name="Название категории", unique=True)
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание категории")

    class Meta:
        db_table = 'categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('category-detail', kwargs={'cat_slug': self.slug})


class Course(models.Model):
    """Курсы"""
    class Status(models.IntegerChoices):
        DRAFT = 0, 'Черновик'
        PUBLISHED = 1, 'Опубликован'

    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='courses',
        verbose_name="Категория"
    )
    title = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, db_index=True, verbose_name="URL")
    description = models.TextField(verbose_name="Краткое описание")
    full_description = models.TextField(blank=True, verbose_name="Полное описание")
    duration_hours = models.IntegerField(verbose_name="Длительность (часы)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    status = models.IntegerField(
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Статус"
    )
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")

    class Meta:
        db_table = 'courses'
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-time_create']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('course-detail-slug', kwargs={'course_slug': self.slug})


class Group(models.Model):
    """Группы"""
    FORMAT_CHOICES = [
        ('offline', 'Очно'),
        ('online', 'Онлайн'),
        ('hybrid', 'Гибридный'),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='groups', verbose_name="Курс")
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='groups', verbose_name="Преподаватель")
    name = models.CharField(max_length=100, verbose_name="Название группы")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, verbose_name="Формат обучения")
    max_students = models.PositiveIntegerField(default=10, verbose_name="Макс. студентов")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        db_table = 'groups'
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.course.title} - {self.name} ({self.get_format_display()})"


class Student(models.Model):
    """Студенты"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='student_profile',
        verbose_name="Пользователь"
    )
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=50, blank=True, verbose_name="Отчество")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(max_length=100, verbose_name="Email", unique=True)
    birth_date = models.DateField(verbose_name="Дата рождения")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации")

    class Meta:
        db_table = 'students'
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def get_full_name(self):
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return ' '.join(parts)
    
    def save(self, *args, **kwargs):
        """Синхронизация с User и назначение роли"""
        
        # Синхронизация данных с User
        if self.user:
            # Копируем данные из Student в User
            if self.first_name:
                self.user.first_name = self.first_name
            if self.last_name:
                self.user.last_name = self.last_name
            if self.email:
                self.user.email = self.email
            self.user.save()
        else:
            # Если пользователь не указан, но есть email - создаем
            if self.email:
                base_username = self.email.split('@')[0]
                username = base_username
                counter = 1
                
                # Уникальное имя пользователя
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=self.email,
                    first_name=self.first_name,
                    last_name=self.last_name
                )
                self.user = user
        
        # Сохраняем студента
        super().save(*args, **kwargs)
        
        # Назначаем роль после сохранения
        if self.user:
            student_group, _ = AuthGroup.objects.get_or_create(name='Студенты')
            self.user.groups.add(student_group)


# === Сигналы для автоматической синхронизации ===

@receiver(post_save, sender=User)
def sync_user_to_profile(sender, instance, created, **kwargs):
    """Синхронизация данных из User в профиль при обновлении пользователя"""
    if hasattr(instance, 'teacher_profile'):
        teacher = instance.teacher_profile
        updated = False
        
        if instance.first_name and teacher.first_name != instance.first_name:
            teacher.first_name = instance.first_name
            updated = True
        if instance.last_name and teacher.last_name != instance.last_name:
            teacher.last_name = instance.last_name
            updated = True
        if instance.email and teacher.email != instance.email:
            teacher.email = instance.email
            updated = True
        
        if updated:
            teacher.save()
    
    elif hasattr(instance, 'student_profile'):
        student = instance.student_profile
        updated = False
        
        if instance.first_name and student.first_name != instance.first_name:
            student.first_name = instance.first_name
            updated = True
        if instance.last_name and student.last_name != instance.last_name:
            student.last_name = instance.last_name
            updated = True
        if instance.email and student.email != instance.email:
            student.email = instance.email
            updated = True
        
        if updated:
            student.save()


class Enrollment(models.Model):
    """Записи на курс"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments', verbose_name="Студент")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='enrollments', verbose_name="Группа")
    enrollment_date = models.DateField(auto_now_add=True, verbose_name="Дата записи")
    is_active = models.BooleanField(default=True, verbose_name="Активная запись")

    class Meta:
        db_table = 'enrollments'
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курсы'
        unique_together = ['student', 'group']

    def __str__(self):
        return f"{self.student} -> {self.group}"


class Schedule(models.Model):
    """Расписание"""
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='schedule', verbose_name="Группа")
    date = models.DateField(verbose_name="Дата занятия")
    time = models.TimeField(verbose_name="Время занятия")
    classroom = models.CharField(max_length=50, verbose_name="Аудитория")
    topic = models.CharField(max_length=200, blank=True, verbose_name="Тема занятия")

    class Meta:
        db_table = 'schedule'
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'
        ordering = ['date', 'time']
        unique_together = ['group', 'date', 'time']  # Нельзя два занятия в одно время у одной группы

    def __str__(self):
        return f"{self.group} - {self.date} {self.time}"


class Attendance(models.Model):
    """Посещаемость"""
    STATUS_CHOICES = [
        ('present', 'Присутствовал'),
        ('absent', 'Отсутствовал'),
        ('late', 'Опоздал'),
        ('excused', 'По уважительной причине'),
    ]

    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='attendance', verbose_name="Занятие")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance', verbose_name="Студент")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='absent', verbose_name="Статус")
    note = models.CharField(max_length=200, blank=True, verbose_name="Примечание")

    class Meta:
        db_table = 'attendance'
        verbose_name = 'Посещаемость'
        verbose_name_plural = 'Посещаемость'
        unique_together = ['schedule', 'student']

    def __str__(self):
        return f"{self.student} - {self.schedule.date} - {self.get_status_display()}"


class Performance(models.Model):
    """Успеваемость"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='performance', verbose_name="Студент")
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='performance', verbose_name="Группа")
    grade = models.CharField(max_length=10, verbose_name="Оценка")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    date = models.DateField(auto_now_add=True, verbose_name="Дата выставления")

    class Meta:
        db_table = 'performance'
        verbose_name = 'Успеваемость'
        verbose_name_plural = 'Успеваемость'
        ordering = ['-date']

    def __str__(self):
        return f"{self.student} - {self.group} - {self.grade}"


class Review(models.Model):
    """Отзывы"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='reviews', verbose_name="Студент")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews', verbose_name="Курс")
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], verbose_name="Оценка")
    comment = models.TextField(verbose_name="Комментарий")
    review_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата отзыва")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрен")

    class Meta:
        db_table = 'reviews'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-review_date']

    def __str__(self):
        return f"Отзыв от {self.student} на курс {self.course}"
    
    
class Administrator(models.Model):
    """Администраторы студии"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='admin_profile',
        verbose_name="Пользователь"
    )
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    position = models.CharField(max_length=100, default="Администратор", verbose_name="Должность")
    
    class Meta:
        db_table = 'administrators'
        verbose_name = 'Администратор'
        verbose_name_plural = 'Администраторы'
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    def get_full_name(self):
        return f"{self.last_name} {self.first_name}"


# Пользовательский менеджер для опубликованных курсов
class PublishedCourseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Course.Status.PUBLISHED)


# Добавляем менеджер к модели Course
Course.add_to_class('published', PublishedCourseManager())