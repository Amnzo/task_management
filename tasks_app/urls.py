from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_kanban, name='task_kanban'),
    path('tasks/<int:task_id>/update_status/', views.update_task_status, name='update_task_status'),
]
