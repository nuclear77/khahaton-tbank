from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='register/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
]