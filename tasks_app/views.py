import traceback
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from django.contrib import messages
from django.db.models import Case, When, Value, IntegerField, Q
from .models import Task, Personne
from .forms import TaskForm, PersonneForm
from django.forms.models import model_to_dict
from django.views.generic import ListView

def task_kanban(request):
    # Vérifier si l'utilisateur est connecté
    if 'user_id' not in request.session:
        return redirect('login')
    
    # Récupérer l'utilisateur connecté
    try:
        current_user = Personne.objects.get(id=request.session['user_id'])
    except Personne.DoesNotExist:
        # Si l'utilisateur n'existe plus, déconnecter et rediriger vers la page de connexion
        if 'user_id' in request.session:
            del request.session['user_id']
        if 'username' in request.session:
            del request.session['username']
        return redirect('login')
    
    # Récupérer les tâches
    tasks = Task.objects.filter(archived=False).annotate(
        priority_order=Case(
            When(priority='HIGH', then=Value(1)),
            When(priority='MEDIUM', then=Value(2)),
            When(priority='LOW', then=Value(3)),
            output_field=IntegerField(),
        )
    ).order_by('priority_order', '-created_at')

    users = Personne.objects.filter(actif=True)

    context = {
        'todo': tasks.filter(status='TO DO'),
        'inprogress': tasks.filter(status='IN PROGRESS'),
        'done': tasks.filter(status='DONE'),
        'users': users,
        'current_user': current_user,
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
    print(f"\n=== Début de la mise à jour de la tâche {task_id} ===")
    print(f"Headers: {dict(request.headers)}")
    print(f"Content-Type: {request.content_type}")
    print(f"Méthode: {request.method}")
    print(f"Utilisateur: {request.user}")
    print(f"Body brut: {request.body}")
    print(f"is_ajax: {request.headers.get('X-Requested-With') == 'XMLHttpRequest'}")
    
    try:
        task = get_object_or_404(Task, pk=task_id)
        print(f"Tâche trouvée: {task}")
    except Exception as e:
        print(f"Erreur lors de la récupération de la tâche: {str(e)}")
        return JsonResponse({'status': 'error', 'message': 'Tâche non trouvée'}, status=404)
    
    if request.method == 'POST':
        try:
            # Essayer de décoder le JSON manuellement pour mieux gérer les erreurs
            try:
                if isinstance(request.body, bytes):
                    body_str = request.body.decode('utf-8')
                else:
                    body_str = request.body
                
                print(f"Corps de la requête (décodé): {body_str}")
                
                # Vérifier si le corps est vide
                if not body_str.strip():
                    print("Erreur: Le corps de la requête est vide")
                    return JsonResponse({
                        'status': 'error',
                        'message': 'Le corps de la requête est vide',
                        'received_data': str(request.body)
                    }, status=400)
                
                data = json.loads(body_str)
                print(f"Données JSON décodées: {data}")
                
                # Vérifier que les champs requis sont présents
                required_fields = ['description', 'priority', 'status']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    print(f"Champs manquants: {missing_fields}")
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Champs manquants: {missing_fields}',
                        'missing_fields': missing_fields
                    }, status=400)
                
            except json.JSONDecodeError as e:
                print(f"Erreur de décodage JSON: {str(e)}")
                return JsonResponse({
                    'status': 'error', 
                    'message': f'Erreur de décodage JSON: {str(e)}',
                    'received_data': str(request.body)[:100]  # Ne logger que les 100 premiers caractères
                }, status=400)
            
            task.description = data.get('description', task.description)
            task.priority = data.get('priority', task.priority)
            task.status = data.get('status', task.status)
            
            print(f"Nouvelles valeurs - Description: {task.description}, Priorité: {task.priority}, Statut: {task.status}")
            
            # Mettre à jour la personne assignée si fournie
            assigned_to_id = data.get('assigned_to')
            if assigned_to_id is not None:
                try:
                    assigned_to = Personne.objects.get(id=assigned_to_id)
                    task.assigned_to = assigned_to
                except Personne.DoesNotExist:
                    return JsonResponse({'status': 'error', 'message': 'Utilisateur non trouvé'}, status=400)
            
            task.save()
            print("Tâche sauvegardée avec succès")
            
            response_data = {
                'status': 'success',
                'message': 'Tâche mise à jour avec succès',
                'task': {
                    'id': task.id,
                    'description': task.description,
                    'priority': task.priority,
                    'status': task.status,
                    'assigned_to': task.assigned_to.nom if task.assigned_to else 'Non assigné',
                    'assigned_to_id': task.assigned_to.id if task.assigned_to else None,
                }
            }
            
            print(f"Réponse envoyée: {response_data}")
            print(f"=== Fin de la mise à jour de la tâche {task_id} ===\n")
            return JsonResponse(response_data)
        except json.JSONDecodeError as e:
            error_msg = f'Données JSON invalides: {str(e)}'
            print(f"ERREUR: {error_msg}")
            return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
        except Exception as e:
            error_msg = f'Erreur lors de la mise à jour: {str(e)}'
            print(f"ERREUR: {error_msg}")
            print(f"Type d'erreur: {type(e).__name__}")
            print(f"Traceback: {traceback.format_exc()}")
            return JsonResponse({'status': 'error', 'message': error_msg}, status=400)
    
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

class ArchivedTaskListView(ListView):
    model = Task
    template_name = 'tasks/archived_tasks.html'
    context_object_name = 'tasks'
    
    def get_queryset(self):
        return Task.objects.filter(archived=True).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_tab'] = 'archived'
        return context


@csrf_exempt
@require_http_methods(["POST"])
def archive_all_done_tasks(request):
    """Vue pour archiver toutes les tâches terminées"""
    print("******************************")
    try:
        # Récupérer et archiver toutes les tâches terminées non archivées
        updated = Task.objects.filter(status='DONE', archived=False).update(archived=True)
        print(updated)
        
        return JsonResponse({
            'status': 'success',
            'message': f'{updated} tâche(s) archivée(s) avec succès',
            'count': updated
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


def user_kanban(request):
    """
    Vue Kanban pour les utilisateurs non-administrateurs
    """
    if 'user_id' not in request.session:
        return redirect('login')
    
    try:
        current_user = Personne.objects.get(id=request.session['user_id'])
    except Personne.DoesNotExist:
        if 'user_id' in request.session:
            del request.session['user_id']
        if 'username' in request.session:
            del request.session['username']
        return redirect('login')
    
    # Récupérer uniquement les tâches de l'utilisateur connecté
    tasks = Task.objects.filter(
        assigned_to=current_user,
        archived=False
    ).annotate(
        priority_order=Case(
            When(priority='HIGH', then=Value(1)),
            When(priority='MEDIUM', then=Value(2)),
            When(priority='LOW', then=Value(3)),
            output_field=IntegerField(),
        )
    ).order_by('priority_order', '-created_at')

    context = {
        'todo': tasks.filter(status='TO DO'),
        'inprogress': tasks.filter(status='IN PROGRESS'),
        'done': tasks.filter(status='DONE'),
        'current_user': current_user,
        'is_admin': False,
    }
    return render(request, 'tasks/user_kanban.html', context)

def login_view(request):
    """
    Vue pour la page de connexion
    Redirige vers la vue appropriée selon le type d'utilisateur
    """
    error = None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        code = request.POST.get('code')
        
        try:
            user = Personne.objects.get(nom__iexact=username, code__iexact=code, actif=True)
            request.session['user_id'] = user.id
            request.session['username'] = user.nom
            
            # Rediriger vers la vue appropriée selon le type d'utilisateur
            if user.niveau == 'ADMIN':
                request.session['is_admin'] = True
                return redirect('task_kanban')
            else:
                request.session['is_admin'] = False
                return redirect('user_kanban')
                
        except Personne.DoesNotExist:
            error = "Nom d'utilisateur ou code incorrect."
        except Exception as e:
            error = f"Une erreur est survenue : {str(e)}"
    
    return render(request, 'tasks/login.html', {'error': error})


def logout_view(request):
    """
    Vue pour la déconnexion
    """
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'username' in request.session:
        del request.session['username']
    return redirect('login')
