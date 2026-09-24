from django.urls import path

from . import views

urlpatterns = [
    path('ogrenciler/', views.student_list, name='student_list'),
    path('ogrenciler/yeni/', views.student_create, name='student_create'),
    path('ogrenciler/<int:student_id>/', views.student_detail, name='student_detail'),
    path('ogrenciler/<int:student_id>/duzenle/', views.student_update, name='student_update'),
    path('ogrenciler/<int:student_id>/gelisim/', views.student_development, name='student_development'),
    path('ogrenciler/<int:student_id>/sil/', views.student_delete, name='student_delete'),
]
