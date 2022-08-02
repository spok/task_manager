from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.views import generic, View
from .models import Task, Project, Comment, Document
from .forms import TaskModelForm, CommentForm


class TaskView(View):
    def get(self, request, pk):
        try:
            current_task = Task.objects.get(id=pk)
            comments = Comment.objects.filter(task=current_task)
            comment_form = CommentForm()
            return render(request,
                          'task.html',
                          context={'task': current_task, 'comments': comments, 'comment_form': comment_form}
                          )
        except Task.DoesNotExist:
            return HttpResponseNotFound('<h2>Задача не найдена</h2>')

    def post(self, request, pk):
        try:
            form = CommentForm(request.POST, request.FILES)
            if form.is_valid():
                current_task = Task.objects.get(id=pk)
                new_comment = Comment()
                new_comment.comment_text = form.cleaned_data['comment_text']
                new_comment.user_added = request.user
                new_comment.save()
                files = request.FILES.getlist('files_added')
                for f in files:
                    instance = Document(file=f, real_name=f)
                    instance.save()
                    new_comment.files_added.add(instance)
                new_comment.save()
                current_task.comments.add(new_comment)
                current_task.save()
        except Task.DoesNotExist:
            return HttpResponseNotFound('<h2>Задача не найдена</h2>')

class TaskListView(View):

    def get(self, request):
        current_user = request.user
        task_list = Task.objects.filter(executor=current_user)
        return render(request, 'task_list.html', context={'object_list': task_list})


class TaskAddView(View):

    def get(self, request):
        task_form = TaskModelForm()
        return render(request,
                      'task_form.html',
                      context={'task_form': task_form}
                      )

    def post(self, request):
        task_form = TaskModelForm(request.POST)
        if task_form.is_valid():
            new_task = task_form.save(commit=False)
            new_task.who_set = request.user
            # Определение номера задачи и корректировка в записи модели проекта последнего номера задачи
            current_project = Project.objects.get(name=new_task.project_name)
            current_project.last_id = current_project.last_id + 1
            current_project.save()
            new_task.current_id = current_project.last_id
            new_task.save()
            task_form.save_m2m()
            return HttpResponseRedirect('tasks')
        else:
            task_form.add_error('__all__', 'Ошибка ввода данных')
        return render(request,
                      'task_form.html',
                      context={'task_form': task_form}
                      )


class TaskEditView(View):

    def get(self, request, pk):
        try:
            # Проверяем чтоб отредактировать запись мог только исполнитель и назначивший задачу
            current_user = request.user
            current_task = Task.objects.get(id=pk)
            if current_user in current_task.executor.all() or current_user == current_task.who_set:
                task_form = TaskModelForm(instance=current_task)
                return render(request, 'task_edit.html', context={"form": task_form, "id": pk})
            else:
                return HttpResponseRedirect('/tasks')
        except Task.DoesNotExist:
            return HttpResponseNotFound('<h2>Задача не найдена</h2>')

    def post(self, request, pk):
        current_task = Task.objects.get(id=pk)
        task_form = TaskModelForm(request.POST, instance=current_task)
        if task_form.is_valid():
            current_task.save()
        return HttpResponseRedirect('/tasks')
