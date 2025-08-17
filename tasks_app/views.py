from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core import serializers
import json

from .models import Task, Personne
from .forms import PersonneForm, TaskForm
from django.forms.models import model_to_dict
from django.contrib import messages


def task_kanban(request):
    tasks = Task.objects.filter(archived=False)
    users = Personne.objects.filter(actif=True)

    context = {
        'todo': tasks.filter(status='TO DO'),
        'inprogress': tasks.filter(status='IN PROGRESS'),
        'done': tasks.filter(status='DONE'),
        'users': users,
    }
    return render(request, 'tasks/kanban.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def update_task_status(request, task_id):
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if not new_status:
            return JsonResponse({'status': 'error', 'message': 'Status is required'}, status=400)
            
        task = get_object_or_404(Task, id=task_id)
        old_status = task.status
        
        # Update the task status
        task.status = new_status
        task.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Task status updated from {old_status} to {new_status}'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def reassign_task(request, task_id):
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        
        task = get_object_or_404(Task, id=task_id)
        
        if user_id:
            user = get_object_or_404(Personne, id=user_id)
            task.assigned_to = user
        else:
            task.assigned_to = None
            
        task.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Task reassigned successfully',
            'assigned_to': task.assigned_to.nom if task.assigned_to else None
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def get_users_json(request):
    """Vue pour récupérer la liste des utilisateurs actifs au format JSON"""
    try:
        users = list(Personne.objects.filter(actif=True).values('id', 'nom'))
        return JsonResponse(users, safe=False)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def update_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            task.description = data.get('description', task.description)
            task.priority = data.get('priority', task.priority)
            task.status = data.get('status', task.status)
            
            # Mettre à jour la personne assignée si fournie
            assigned_to_id = data.get('assigned_to')
            if assigned_to_id is not None:
                try:
                    assigned_to = Personne.objects.get(id=assigned_to_id)
                    task.assigned_to = assigned_to
                except Personne.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Utilisateur non trouvé'}, status=400)
            
            task.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Tâche mise à jour avec succès',
                'task': {
                    'id': task.id,
                    'description': task.description,
                    'priority': task.priority,
                    'status': task.status,
                    'assigned_to': task.assigned_to.get_full_name() if task.assigned_to else 'Non assigné',
                    'assigned_to_id': task.assigned_to.id if task.assigned_to else None,
                }
            })
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Données JSON invalides'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Méthode non autorisée'}, status=405)


def user_create(request):
    if request.method == 'POST':
        form = PersonneForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur créé avec succès')
            return redirect('task_kanban')
    else:
        form = PersonneForm()
    
    return render(request, 'tasks/user_form.html', {
        'form': form,
        'title': 'Nouvel utilisateur'
    })


def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            # Récupérer ou créer une instance Personne correspondant à l'utilisateur connecté
            # Ici, on suppose que le nom d'utilisateur correspond au champ 'nom' dans Personne
            # Vous devrez peut-être adapter cette logique selon votre modèle d'authentification
            username = request.user.username
            personne, created = Personne.objects.get_or_create(
                nom=username,
                defaults={
                    'code': username.upper(),
                    'actif': True,
                    'niveau': 'user-simple'
                }
            )
            task.created_by = personne
            task.save()
            messages.success(request, 'Tâche créée avec succès')
            return redirect('task_kanban')
    else:
        form = TaskForm()
    
    return render(request, 'tasks/task_form.html', {
        'form': form,
        'title': 'Nouvelle tâche'
    })
