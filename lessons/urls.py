from django.urls import path

from . import views

urlpatterns = [
    path('takvim/', views.calendar_view, name='calendar'),
    path('dersler/', views.lesson_list, name='lesson_list'),
    path('dersler/yeni/', views.lesson_create, name='lesson_create'),
    path('dersler/<int:lesson_id>/', views.lesson_detail, name='lesson_detail'),
    path('dersler/<int:lesson_id>/yoklama/', views.attendance_update, name='attendance_update'),
]
