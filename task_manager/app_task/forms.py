from django import forms
from django.forms import ModelForm
from .models import Task, Status, Priority, Project, Comment
from django.contrib.auth.models import User


class TaskModelForm(ModelForm):
    class Meta:
        model = Task
        fields = ['name', 'description', 'date_completion', 'executor', 'status', 'priority', 'project_name']


class CommentForm(forms.Form):
    comment_text = forms.CharField(max_length=300, label='Текст комментария', widget=forms.Textarea)
    files_added = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
