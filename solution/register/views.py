from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.apps import apps

from .forms import RegisterForm
from .models import UserProfile


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                'Регистрация прошла успешно! Добро пожаловать!'
            )
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, "register/register.html", {"form": form})


def custom_login(request):
    """Кастомный вход в систему."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, "register/login.html")


@login_required
def profile(request):
    user = request.user
    user_profile, created = UserProfile.objects.get_or_create(user=user)

    Dish = apps.get_model('app', 'Dish')
    liked_dishes = user_profile.liked_dishes.all()

    initials = get_user_initials(user)

    context = {
        'user': user,
        'user_profile': user_profile,
        'liked_dishes': liked_dishes,
        'initials': initials,
        'user_name': user.get_full_name() or user.username,
    }
    return render(request, 'register/profile.html', context)


def custom_logout(request):
    """Кастомный выход из системы с перенаправлением на главную страницу."""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы.')
    return redirect('home')


def get_user_initials(user):
    """Получить инициалы пользователя для аватара."""
    if user.first_name and user.last_name:
        return f"{user.first_name[0]}{user.last_name[0]}".upper()
    elif user.first_name:
        return user.first_name[0].upper()
    else:
        return user.username[0].upper()