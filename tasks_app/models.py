from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone


class Personne(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True, null=True)
    actif = models.BooleanField(default=True)
    niveau = models.CharField(
        max_length=20,
        choices=(
            ('ADMIN', 'ADMIN'),
            ('USER-SIMPLE', 'UTILISATEUR SIMPLE'),
        ),
        default='USER-SIMPLE'
)

    def __str__(self):
        return f"{self.nom}, {self.id}"


class Task(models.Model):
    STATUS_CHOICES = (
        ('TO DO', 'À FAIRE'),
        ('IN PROGRESS', 'EN COURS'),
        ('DONE', 'TERMINÉE'),
    )

    PRIORITY_CHOICES = (
        ('HIGH', 'H'),
        ('MEDIUM', 'M'),
        ('LOW', 'L'),
    )

    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='TO DO')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    created_by = models.ForeignKey(
        'Personne',
        related_name='tasks_created',
        on_delete=models.CASCADE
    )
    assigned_to = models.ForeignKey(
        'Personne',
        related_name='tasks_assigned',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.description[:30]}... ({self.get_status_display()} - {self.get_priority_display()})"