from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit-profile'),
    path('dashboard/', views.dashboard_redirect, name='dashboard'),  # Теперь функция существует
    path('dashboard/student/', views.student_dashboard, name='student-dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher-dashboard'),
    path('dashboard/marketer/', views.marketer_dashboard, name='marketer-dashboard'),
]