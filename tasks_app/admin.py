from django.contrib import admin
from .models import Task, Personne

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('description', 'status', 'created_by', 'assigned_to', 'created_at', 'archived')
    list_filter = ('status', 'archived', 'created_at')
    search_fields = ('description', 'created_by__nom', 'assigned_to__nom')
    date_hierarchy = 'created_at'

@admin.register(Personne)
class PersonneAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code', 'niveau', 'actif')
    list_filter = ('niveau', 'actif')
    search_fields = ('nom', 'code')
