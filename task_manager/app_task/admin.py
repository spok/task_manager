from django.contrib import admin
from .models import Status, Priority, Project, Task, Comment, Document


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    pass


@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['comment_text', 'user_added', 'date_publication']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['file', 'real_name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'date_completion', 'who_set', 'status', 'priority', 'project_name']
    exclude = ("current_id", )
