from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_kanban, name='task_kanban'),
    path('tasks/<int:task_id>/update_status/', views.update_task_status, name='update_task_status'),
    path('tasks/<int:task_id>/reassign/', views.reassign_task, name='reassign_task'),
    path('get_users/', views.get_users_json, name='get_users_json'),
    path('tasks/<int:task_id>/update/', views.update_task, name='update_task'),
]
