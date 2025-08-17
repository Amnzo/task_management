from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Task, Personne


def task_kanban(request):
    tasks = Task.objects.filter(archived=False)

    context = {
        'todo': tasks.filter(status='TO DO'),
        'inprogress': tasks.filter(status='IN PROGRESS'),
        'done': tasks.filter(status='DONE'),
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
