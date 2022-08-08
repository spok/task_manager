from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.shortcuts import render
from django.views import generic, View
from django.contrib.auth.models import User
from .models import Task, Project, Comment, Document, Logger
from .forms import TaskModelForm, CommentForm


def add_log(user, task, text):
    """
    Сохранение лога в базу данных
    :param user: id пользователя
    :param task: id задачи
    :param text: описание действия
    :return: None
    """
    new_log = Logger()
    new_log.user = user
    new_log.task = task
    new_log.text = text
    new_log.save()

class TaskView(View):
    def get(self, request, pk):
        try:
            current_task = Task.objects.get(id=pk)
            comments = Comment.objects.filter(task=current_task)
            comments_list = []
            for comm in comments:
                comm_dict = dict()
                comm_dict['text'] = comm.comment_text
                comm_dict['id'] = comm.id
                comm_dict['user'] = comm.user_added
                comm_dict['date'] = comm.date_publication
                comm_dict['files'] = Document.objects.filter(comment=comm)
                comments_list.append(comm_dict)
            comment_form = CommentForm()
            return render(request,
                          'task.html',
                          context={'task': current_task, 'comments': comments_list, 'comment_form': comment_form}
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
                add_log(request.user, current_task, 'добавил(а) комментарий')
                return HttpResponseRedirect(f'/task/{pk}')

        except Task.DoesNotExist:
            return HttpResponseNotFound('<h2>Задача не найдена</h2>')

class TaskListView(View):

    def get(self, request):
        current_user = request.user
        get_archive = request.GET.get("archive", "")
        if get_archive:
            task_list = Task.objects.filter(executor=current_user, in_archive=True)
        else:
            task_list = Task.objects.filter(executor=current_user, in_archive=False)
        print(task_list)
        log_list = Logger.objects.all()[:5]
        return render(request, 'task_list.html', context={'object_list': task_list,
                                                          'user': current_user, 'log_list': log_list})


class TaskAddView(View):

    def get(self, request):
        task_form = TaskModelForm()
        return render(request,
                      'task_form.html',
                      context={'task_form': task_form, 'title': 'Новая задача'}
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
            add_log(request.user, new_task, 'добавил(а) задачу')
            return HttpResponseRedirect('/tasks')
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
            add_log(request.user, current_task, 'редактировал(а) задачу')
        return HttpResponseRedirect('/tasks')


class TaskArchivView(View):
    def get(self, request, id):
        # Переводим задачу в архив
        current_user = request.user
        current_task = Task.objects.get(id=id)
        current_task.in_archive = True
        current_task.save()
        add_log(request.user, current_task, 'отправил(а) задачу в архив')
        return HttpResponseRedirect('/tasks')


class LogView(View):
    def get(self, request):
        # Вывод истории действий
        log_list = Logger.objects.all()
        current_user = request.user
        return render(request, 'log.html', context={'user': current_user, 'log_list': log_list})


class CommentDelete(View):

    def get(self, request, id):
        comment = Comment.objects.get(id=id)
        current_task = Task.objects.get(comments=comment)
        current_id = current_task.id
        comment.delete()
        add_log(request.user, current_task, 'удалил(а) комментарий к задаче')
        return HttpResponseRedirect(f'/task/{current_id}')
