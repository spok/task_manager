from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from .forms import AuthForm


def login_view(request):
    if request.method == 'POST':
        auth_form = AuthForm(request.POST)
        if auth_form.is_valid():
            username = auth_form.cleaned_data['username']
            password = auth_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return HttpResponseRedirect('tasks')
                else:
                    auth_form.add_error('__all__', 'Ошибка входа.')
            else:
                auth_form.add_error('__all__', 'Ошибка ввода логина или пароля пользователя')
    else:
        auth_form = AuthForm()
    return render(request, 'login.html', context={"form": auth_form})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')
