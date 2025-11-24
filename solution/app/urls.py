from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    # Основные страницы
    path('', views.home, name='home'),
    path('catalog/', views.catalog, name='catalog'),
    path('recipes/', views.recipes, name='recipes'),

    # Меню и планирование
    path('menu/', views.menu, name='menu'),
    path('menu/update/', views.update_daily_menu, name='update_daily_menu'),
    path('menu/get/', views.get_daily_menu, name='get_daily_menu'),

    # Кухни и блюда
    path('cuisine/<int:cuisine_id>/', views.cuisine_detail, name='cuisine_detail'),
    path('dish/<int:dish_id>/', views.dish_detail, name='dish_detail'),

    # Избранные блюда
    path('dish/<int:dish_id>/', views.dish_detail, name='dish_detail'),
    path('dish/<int:dish_id>/toggle_like/', views.toggle_like_dish, name='toggle_like_dish'),

    # Холодильник
    path('fridge/', views.fridge, name='fridge'),
    path('fridge/add/', views.add_to_fridge, name='add_to_fridge'),
    path('fridge/remove/', views.remove_from_fridge, name='remove_from_fridge'),
    path('fridge/recommendations/', views.get_fridge_recommendations, name='fridge_recommendations'),

    # Новые функции холодильника
    path('fridge/add-from-dish/<int:dish_id>/', views.add_ingredients_from_dish, name='add_ingredients_from_dish'),
    path('fridge/quick-add/', views.fridge_quick_add, name='fridge_quick_add'),

    # Обработчики ошибок
    path('404/', views.custom_404, name='custom_404'),
    path('500/', views.custom_500, name='custom_500'),

    # Перенаправления для аутентификации
    path('accounts/login/', RedirectView.as_view(url='/auth/login/', permanent=False)),
    path('accounts/logout/', RedirectView.as_view(url='/auth/logout/', permanent=False)),
    path('accounts/register/', RedirectView.as_view(url='/auth/register/', permanent=False)),
    path('accounts/profile/', RedirectView.as_view(url='/auth/profile/', permanent=False)),

    # Список покупок
    path('shopping-list/', views.shopping_list, name='shopping_list'),
    path('shopping-list/add/', views.add_to_shopping_list, name='add_to_shopping_list'),
    path('shopping-list/add-from-dish/<int:dish_id>/', views.add_dish_ingredients_to_shopping_list, name='add_dish_ingredients_to_shopping_list'),
    path('shopping-list/toggle/', views.toggle_shopping_item, name='toggle_shopping_item'),
    path('shopping-list/remove/', views.remove_shopping_item, name='remove_shopping_item'),
    path('shopping-list/clear/', views.clear_shopping_list, name='clear_shopping_list'),
    path('shopping-list/add-single/', views.add_single_ingredient_to_shopping_list, name='add_single_ingredient_to_shopping_list'),
]