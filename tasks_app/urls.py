from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    # Page d'accueil (connexion)
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Pages protégées par authentification
    path('kanban/', login_required(views.task_kanban), name='task_kanban'),
    path('mes-taches/', login_required(views.user_kanban), name='user_kanban'),
    path('tasks/<int:task_id>/update_status/', login_required(views.update_task_status), name='update_task_status'),
    path('tasks/<int:task_id>/reassign/', login_required(views.reassign_task), name='reassign_task'),
    path('get_users/', login_required(views.get_users_json), name='get_users_json'),
    path('tasks/<int:task_id>/update/', login_required(views.update_task), name='update_task'),
    path('tasks/new/', login_required(views.task_create), name='task_create'),
    path('users/new/', login_required(views.user_create), name='user_create'),
    path('mes-taches/nouvelle/', login_required(views.user_task_create), name='user_task_create'),
    path('tasks/<int:task_id>/archive/', login_required(views.archive_task), name='archive_task'),
    path('archived/', login_required(views.ArchivedTaskListView.as_view()), name='archived_tasks'),
    path('archive_all_done/', login_required(views.archive_all_done_tasks), name='archive_all_done'),
]
