from django.urls import path
from . import views
from .views import TaskListView, TaskView, TaskAddView, TaskEditView, CommentDelete


urlpatterns = [
    path("tasks", TaskListView.as_view(), name='task_list'),
    path("task/<int:pk>", TaskView.as_view(), name='task'),
    path("task/<int:pk>/edit", TaskEditView.as_view(), name='task_edit'),
    path("task_add", TaskAddView.as_view(), name='task_add'),
    path("comment/<int:id>/delete", CommentDelete.as_view(), name="comment_delete"),
]
