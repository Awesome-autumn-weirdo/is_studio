from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Teacher(models.Model):
    """Преподаватели"""
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=50, blank=True, verbose_name="Отчество")
    specialization = models.CharField(max_length=100, verbose_name="Специализация")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(max_length=100, blank=True, verbose_name="Email")  # Добавим email
    bio = models.TextField(blank=True, verbose_name="Биография")  # Добавим биографию
    photo = models.ImageField(upload_to='teachers/%Y/%m/', blank=True, null=True, verbose_name="Фото")
    is_active = models.BooleanField(default=True, verbose_name="Активен")  # Добавим статус

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='student_profile')
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


# Пользовательский менеджер для опубликованных курсов
class PublishedCourseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Course.Status.PUBLISHED)


# Добавляем менеджер к модели Course
Course.add_to_class('published', PublishedCourseManager())