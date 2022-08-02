from django.db import models
from django.contrib.auth.models import User


def get_name(self):
    if self.first_name or self.last_name:
        return '{} {}'.format(self.last_name, self.first_name)
    else:
        return self.username

User.add_to_class("__str__", get_name)


# Модель статуса задачи
class Status(models.Model):
    name = models.CharField(max_length=30, verbose_name='Статусы задач', default='Поставлена')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'


# Модель приоритета задачи
class Priority(models.Model):
    name = models.SmallIntegerField(verbose_name='Приоритеты задач', default=1)

    def __str__(self):
        priority_text = ('Низкий', 'Нормальный', 'Высокий', 'Очень высокий')
        if self.name > 3:
            self.name = 3
        return priority_text[self.name]

    class Meta:
        ordering = ['-name']
        verbose_name = 'Приоритет задачи'
        verbose_name_plural = 'Приоритеты задач'


# Модель проектов
class Project(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название проекта')
    last_id = models.IntegerField(default=0, verbose_name='Номер последней задачи по проекту')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'


# Модель файлов
class Document(models.Model):
    file = models.FileField(upload_to='documents/', verbose_name='Внутреннее имя файла')
    real_name = models.CharField(max_length=300, verbose_name='Реальное имя файла')

    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'


# Модель комментарий к задачам
class Comment(models.Model):
    comment_text = models.CharField(max_length=300, verbose_name='Комментарий')
    user_added = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Пользователь')
    date_publication = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время комментария')
    files_added = models.ManyToManyField(Document, null=True, blank=True, verbose_name='Файлы')

    def __str__(self):
        return self.comment_text

    class Meta:
        ordering = ['date_publication']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


# Модель задачи
class Task(models.Model):
    name = models.CharField(max_length=100, verbose_name='Краткое описание задачи')
    current_id = models.IntegerField(default=1)
    description = models.TextField(verbose_name='Подробное описание задачи', null=True)
    date_completion = models.DateTimeField(verbose_name='Дата и время завершения задачи')
    date_update = models.DateTimeField(auto_now=True, verbose_name='Дата и время последнего обновления задачи')
    date_statement = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время постановки задачи')
    in_archive = models.BooleanField(default=False, verbose_name='Задача в архиве')
    who_set = models.ForeignKey(User, default=None, null=True, blank=True, verbose_name='Создатель задачи',
                                    on_delete=models.SET_NULL, related_name='user_who_set')
    executor = models.ManyToManyField(User, default=None, verbose_name='Назначенные исполнители',
                                      related_name='user_executor')
    status = models.ForeignKey(Status, on_delete=models.SET_NULL,
                               null=True, verbose_name='Текущий статус')
    priority = models.ForeignKey(Priority, on_delete=models.SET_NULL, null=True, verbose_name='Приоритет')
    project_name = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, verbose_name='Проект')
    comments = models.ManyToManyField(Comment, verbose_name='Комментарии')

    def __str__(self):
        return f'Задача № {self.current_id} - {self.name}'

    class Meta:
        ordering = ['-priority', 'date_statement']
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

