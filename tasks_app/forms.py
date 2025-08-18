from django import forms
from django.core.validators import RegexValidator
from .models import Task, Personne

class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].widget.attrs.update({
            'class': 'form-control text-uppercase',
            'rows': 3,
            'oninput': 'this.value = this.value.toUpperCase()',
            'style': 'text-transform: uppercase'
        })
        self.fields['status'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['priority'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['assigned_to'].widget.attrs.update({
            'class': 'form-select'
        })

    class Meta:
        model = Task
        fields = ['description', 'status', 'priority', 'assigned_to']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
        }
    
    def clean_description(self):
        return self.cleaned_data['description'].upper()

class PersonneForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nom'].widget.attrs.update({
            'class': 'form-control text-uppercase',
            'oninput': 'this.value = this.value.toUpperCase()',
            'style': 'text-transform: uppercase'
        })
        self.fields['code'].widget.attrs.update({
            'class': 'form-control text-uppercase',
            'oninput': 'this.value = this.value.toUpperCase()',
            'style': 'text-transform: uppercase',
            'pattern': '[A-Z0-9]+',
            'title': 'Veuillez utiliser uniquement des lettres majuscules et des chiffres'
        })
        self.fields['niveau'].widget.attrs.update({
            'class': 'form-select'
        })

    class Meta:
        model = Personne
        fields = ['nom', 'code', 'niveau', 'actif']
        widgets = {
            'actif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'nom': 'NOM COMPLET',
            'code': 'CODE D\'ACCÈS',
            'niveau': 'NIVEAU D\'ACCÈS',
            'actif': 'COMPTE ACTIF',
        }
    
    def clean_nom(self):
        return self.cleaned_data['nom'].upper()
    
    def clean_code(self):
        code = self.cleaned_data['code'].upper()
        if not code.isalnum():
            raise forms.ValidationError("Le code ne doit contenir que des lettres et des chiffres.")
        return code
