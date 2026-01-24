from django.utils import timezone
from datetime import date
from django.db.models import Q
from .models import DailyMenu, Dish, ShoppingList, Cuisine, FridgeItem, ShoppingListItem
from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
import re


# Импортируем UserProfile через apps.get_model для избежания циклических импортов
def get_user_profile(user):
    from django.apps import apps
    UserProfile = apps.get_model('register', 'UserProfile')
    profile, created = UserProfile.objects.get_or_create(user=user)
    return profile


# Вспомогательные функции для работы с ингредиентами
def normalize_ingredient(ingredient):
    """Нормализует название ингредиента для сравнения"""
    if not ingredient:
        return ""
    # Приводим к нижнему регистру и убираем лишние пробелы
    ingredient = ingredient.lower().strip()
    # Удаляем единицы измерения и цифры
    ingredient = re.sub(r'\d+[.,]?\d*\s*(г|кг|мл|л|шт|ст|ч\.л|ст\.л|зубч|пучок|щепотка|по вкусу)', '', ingredient)
    # Удаляем лишние символы
    ingredient = re.sub(r'[^\w\sа-яё]', ' ', ingredient)
    # Убираем лишние пробелы
    ingredient = ' '.join(ingredient.split())
    return ingredient


def get_ingredient_keywords(ingredient):
    """Извлекает ключевые слова из ингредиента"""
    normalized = normalize_ingredient(ingredient)
    if not normalized:
        return []

    # Список стоп-слов для исключения
    stop_words = {'свежий', 'свежая', 'свежее', 'свежие', 'молотый', 'молотая', 'молотое',
                  'сушеный', 'сушеная', 'сушеное', 'консервированный', 'консервированная',
                  'консервированное', 'нарезанный', 'нарезанная', 'нарезанное', 'мелкий',
                  'мелкая', 'мелкое', 'крупный', 'крупная', 'крупное', 'очищенный',
                  'очищенная', 'очищенное', 'тертый', 'тертая', 'тертое', 'по', 'вкусу'}

    words = normalized.split()
    # Фильтруем стоп-слова и короткие слова
    keywords = [word for word in words if word not in stop_words and len(word) > 2]
    return keywords


def calculate_ingredient_match(user_ingredients, dish_ingredients):
    """Рассчитывает процент совпадения ингредиентов"""
    if not dish_ingredients:
        return 0

    user_keywords = set()
    for ingredient in user_ingredients:
        user_keywords.update(get_ingredient_keywords(ingredient))

    if not user_keywords:
        return 0

    matching_keywords = 0
    total_dish_keywords = 0

    for dish_ingredient in dish_ingredients:
        dish_keywords = set(get_ingredient_keywords(dish_ingredient))
        total_dish_keywords += len(dish_keywords)

        for dish_keyword in dish_keywords:
            for user_keyword in user_keywords:
                # Проверяем различные варианты совпадения
                if (user_keyword in dish_keyword or
                        dish_keyword in user_keyword or
                        user_keyword[:4] == dish_keyword[:4]):  # Проверка по первым 4 символам
                    matching_keywords += 1
                    break

    if total_dish_keywords == 0:
        return 0

    match_percentage = (matching_keywords / total_dish_keywords) * 100
    return min(match_percentage, 100)  # Ограничиваем 100%


def get_missing_ingredients(user_ingredients, dish_ingredients):
    """Определяет недостающие ингредиенты для блюда"""
    user_keywords = set()
    for ingredient in user_ingredients:
        user_keywords.update(get_ingredient_keywords(ingredient))

    missing = []
    for dish_ingredient in dish_ingredients:
        dish_keywords = set(get_ingredient_keywords(dish_ingredient))
        has_match = False

        for dish_keyword in dish_keywords:
            for user_keyword in user_keywords:
                if (user_keyword in dish_keyword or
                        dish_keyword in user_keyword or
                        user_keyword[:4] == dish_keyword[:4]):
                    has_match = True
                    break
            if has_match:
                break

        if not has_match and dish_ingredient.strip():
            missing.append(dish_ingredient.strip())

    return missing


def get_recommended_dishes(user):
    """Логика рекомендаций блюд на основе продуктов в холодильнике"""
    # Получаем все продукты пользователя в холодильнике
    user_ingredients = list(FridgeItem.objects.filter(user=user).values_list('name', flat=True))

    # Получаем все блюда с предзагрузкой связанных данных
    all_dishes = Dish.objects.all().select_related('cuisine')

    recommended_dishes = []

    for dish in all_dishes:
        dish_ingredients = dish.get_ingredients_list()
        if not dish_ingredients:
            continue

        # Рассчитываем процент совпадения
        match_percentage = calculate_ingredient_match(user_ingredients, dish_ingredients)

        # Сохраняем блюда с хотя бы 40% совпадением
        if match_percentage >= 40:
            # Добавляем атрибуты к объекту блюда
            dish.match_percentage = round(match_percentage)
            dish.missing_ingredients = get_missing_ingredients(user_ingredients, dish_ingredients)
            dish.missing_count = len(dish.missing_ingredients)
            recommended_dishes.append(dish)

    # Сортируем блюда по проценту совпадения (по убыванию) и количеству недостающих ингредиентов
    recommended_dishes.sort(key=lambda x: (x.match_percentage, -x.missing_count), reverse=True)

    return {
        'dishes': recommended_dishes[:12],
        'user_ingredients': user_ingredients
    }


def detect_ingredient_category(ingredient_name):
    """Автоматически определяет категорию ингредиента по названию"""
    ingredient_lower = ingredient_name.lower()

    if any(word in ingredient_lower for word in
           ['овощ', 'картофель', 'морковь', 'лук', 'помидор', 'огурец', 'капуст', 'свекл', 'редис', 'баклажан',
            'кабачок', 'перец', 'чеснок']):
        return 'vegetables'
    elif any(word in ingredient_lower for word in
             ['фрукт', 'яблоко', 'банан', 'апельсин', 'лимон', 'груш', 'персик', 'виноград', 'манго', 'апельсин']):
        return 'fruits'
    elif any(word in ingredient_lower for word in
             ['мясо', 'куриц', 'говядин', 'свинин', 'баранин', 'индейк', 'фарш', 'колбас', 'сосиск', 'ветчин']):
        return 'meat'
    elif any(word in ingredient_lower for word in
             ['рыба', 'лосось', 'тунец', 'креветк', 'кальмар', 'миди', 'икра', 'семга', 'окунь']):
        return 'fish'
    elif any(word in ingredient_lower for word in
             ['молок', 'сыр', 'творог', 'сметан', 'йогурт', 'кефир', 'масло сливоч', 'сливки', 'йогурт']):
        return 'dairy'
    elif any(word in ingredient_lower for word in
             ['круп', 'рис', 'гречк', 'макарон', 'мука', 'хлеб', 'булка', 'лапш', 'овес', 'пшено']):
        return 'grains'
    elif any(word in ingredient_lower for word in
             ['специ', 'соль', 'перец', 'трав', 'лавров', 'кориц', 'ванил', 'имбирь', 'куркум', 'паприк']):
        return 'spices'
    elif any(word in ingredient_lower for word in
             ['напиток', 'сок', 'вода', 'чай', 'кофе', 'лимонад', 'компот', 'морс']):
        return 'beverages'
    else:
        return 'other'


# Основные представления
def home(request):
    cuisines = Cuisine.objects.all()[:8]
    dishes = Dish.objects.all()[:8]

    # Получаем избранные блюда для авторизованного пользователя
    liked_dishes_ids = []
    if request.user.is_authenticated:
        user_profile = get_user_profile(request.user)
        liked_dishes_ids = list(user_profile.liked_dishes.values_list('id', flat=True))

    context = {
        'cuisines': cuisines,
        'dishes': dishes,
        'liked_dishes_ids': liked_dishes_ids,
    }

    return render(request, 'app/home.html', context)

def catalog(request):
    cuisines = Cuisine.objects.all()
    return render(request, 'app/catalog.html', {'cuisines': cuisines})


def recipes(request):
    # Получаем все блюда
    dishes = Dish.objects.all().select_related('cuisine')

    # Получаем избранные блюда для авторизованного пользователя
    liked_dishes_ids = []
    if request.user.is_authenticated:
        user_profile = get_user_profile(request.user)
        liked_dishes_ids = list(user_profile.liked_dishes.values_list('id', flat=True))

    # Обработка поиска
    search_query = request.GET.get('search', '')
    if search_query:
        dishes = dishes.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(ingredients__icontains=search_query) |
            Q(cuisine__name__icontains=search_query)
        )

    # Обработка фильтрации по кухне
    cuisine_filter = request.GET.get('cuisine', '')
    if cuisine_filter:
        dishes = dishes.filter(cuisine__name=cuisine_filter)

    # Обработка фильтрации по сложности
    difficulty_filter = request.GET.get('difficulty', '')
    if difficulty_filter:
        dishes = dishes.filter(difficulty=difficulty_filter)

    # Пагинация - исправлена ошибка в названии переменной
    paginator = Paginator(dishes, 12)  # Было pagination = Paginator(dishes, per_page: 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Получаем все кухни для фильтра
    all_cuisines = Cuisine.objects.all()

    context = {
        'dishes': page_obj,
        'page_obj': page_obj,
        'liked_dishes_ids': liked_dishes_ids,
        'all_cuisines': all_cuisines,
        'search_query': search_query,
        'selected_cuisine': cuisine_filter,
        'selected_difficulty': difficulty_filter,
    }

    return render(request, 'app/recipes.html', context)
@login_required
def menu(request):
    now = timezone.now()
    year = request.GET.get('year', now.year)
    month = request.GET.get('month', now.month)

    user_menus = DailyMenu.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month
    )

    menu_dict = {menu.date.day: menu for menu in user_menus}

    # Получаем избранные блюда
    liked_dishes_ids = []
    if request.user.is_authenticated:
        user_profile = get_user_profile(request.user)
        liked_dishes_ids = list(user_profile.liked_dishes.values_list('id', flat=True))

    context = {
        'current_year': int(year),
        'current_month': int(month),
        'menu_dict': menu_dict,
        'dishes': Dish.objects.all()[:10],  # Исправлено: было bish, должно быть Dish
        'liked_dishes_ids': liked_dishes_ids,
    }

    return render(request, 'app/menu.html', context)

# Представления для холодильника
@login_required
def fridge(request):
    """Представление для холодильника"""
    fridge_items = FridgeItem.objects.filter(user=request.user).order_by('category', 'name')

    # Получаем рекомендованные блюда
    recommended_dishes = get_recommended_dishes(request.user)

    # Получаем избранные блюда
    liked_dishes_ids = []
    if request.user.is_authenticated:
        user_profile = get_user_profile(request.user)
        liked_dishes_ids = list(user_profile.liked_dishes.values_list('id', flat=True))  # Исправлено: было Liked_dishes, должно быть liked_dishes

    context = {
        'fridge_items': fridge_items,
        'recommended_dishes': recommended_dishes,
        'liked_dishes_ids': liked_dishes_ids,
    }
    return render(request, 'app/fridge.html', context)

@login_required
@require_POST
def add_to_fridge(request):
    """Добавление продукта в холодильник"""
    ingredient_name = request.POST.get('ingredient', '').strip()

    if not ingredient_name:
        return JsonResponse({'success': False, 'error': 'Название продукта не может быть пустым'})

    try:
        # Определяем категорию автоматически
        category = detect_ingredient_category(ingredient_name)

        # Создаем новый продукт в холодильнике
        fridge_item = FridgeItem.objects.create(
            user=request.user,
            name=ingredient_name,
            category=category
        )

        return JsonResponse({
            'success': True,
            'message': 'Продукт добавлен в холодильник',
            'item_id': fridge_item.id,
            'item_name': fridge_item.name
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def add_ingredients_from_dish(request, dish_id):
    """Добавление всех ингредиентов блюда в холодильник"""
    try:
        dish = get_object_or_404(Dish, id=dish_id)
        ingredients = dish.get_ingredients_list()

        added_count = 0
        skipped_count = 0

        for ingredient in ingredients:
            if ingredient.strip():
                # Определяем категорию
                category = detect_ingredient_category(ingredient)

                # Проверяем, нет ли уже такого продукта
                existing_item = FridgeItem.objects.filter(
                    user=request.user,
                    name=ingredient.strip()
                ).first()

                if not existing_item:
                    FridgeItem.objects.create(
                        user=request.user,
                        name=ingredient.strip(),
                        category=category
                    )
                    added_count += 1
                else:
                    skipped_count += 1

        message = f'Добавлено {added_count} ингредиентов в холодильник'
        if skipped_count > 0:
            message += f' ({skipped_count} уже были в холодильнике)'

        return JsonResponse({
            'success': True,
            'message': message,
            'added_count': added_count,
            'skipped_count': skipped_count
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def remove_from_fridge(request):
    """Удаление продукта из холодильника"""
    item_id = request.POST.get('item_id')

    try:
        fridge_item = get_object_or_404(FridgeItem, id=item_id, user=request.user)
        fridge_item.delete()

        return JsonResponse({'success': True, 'message': 'Продукт удален из холодильника'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def get_fridge_recommendations(request):
    """Получение рекомендованных рецептов на основе продуктов в холодильнике"""
    try:
        recommended_dishes = get_recommended_dishes(request.user)

        dishes_data = []
        for dish in recommended_dishes['dishes']:
            dishes_data.append({
                'id': dish.id,
                'name': dish.name,
                'description': dish.description[:100] + '...' if len(dish.description) > 100 else dish.description,
                'cooking_time': dish.cooking_time,
                'difficulty': dish.get_difficulty_display(),
                'match_percentage': dish.match_percentage
            })

        return JsonResponse({
            'success': True,
            'dishes': dishes_data,
            'user_ingredients': recommended_dishes['user_ingredients']
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def fridge_quick_add(request):
    """Быстрое добавление распространенных ингредиентов"""
    common_ingredients = request.POST.getlist('common_ingredients[]')

    if not common_ingredients:
        return JsonResponse({'success': False, 'error': 'Не выбраны ингредиенты'})

    added_items = []
    for ingredient in common_ingredients:
        if ingredient.strip():
            # Определяем категорию
            category = detect_ingredient_category(ingredient)

            # Проверяем, нет ли уже такого продукта
            existing_item = FridgeItem.objects.filter(
                user=request.user,
                name=ingredient.strip()
            ).first()

            if not existing_item:
                fridge_item = FridgeItem.objects.create(
                    user=request.user,
                    name=ingredient.strip(),
                    category=category
                )
                added_items.append(fridge_item.name)

    return JsonResponse({
        'success': True,
        'message': f'Добавлено {len(added_items)} ингредиентов',
        'added_items': added_items
    })


# Остальные представления
def cuisine_detail(request, cuisine_id):
    """Детальная страница кухни с блюдами"""
    try:
        cuisine = get_object_or_404(Cuisine, id=cuisine_id)  # Исправлено: было Сuisine (русская С), должно быть Cuisine (английская C)
        dishes = Dish.objects.filter(cuisine=cuisine)

        # Получаем избранные блюда для авторизованного пользователя
        liked_dishes_ids = []
        if request.user.is_authenticated:
            user_profile = get_user_profile(request.user)
            liked_dishes_ids = list(user_profile.liked_dishes.values_list('id', flat=True))

        return render(request, 'app/cuisine_detail.html', {
            'cuisine': cuisine,
            'dishes': dishes,
            'liked_dishes_ids': liked_dishes_ids,
        })
    except Exception as e:
        print(f"Error in cuisine_detail: {e}")
        raise Http404("Кухня не найдена")

def dish_detail(request, dish_id):
    """Детальная страница блюда"""
    try:
        dish = get_object_or_404(Dish, id=dish_id)

        # Получаем избранные блюда для авторизованного пользователя
        is_liked = False
        if request.user.is_authenticated:
            user_profile = get_user_profile(request.user)
            is_liked = dish in user_profile.liked_dishes.all()

        return render(request, 'app/dish_detail.html', {
            'dish': dish,
            'is_liked': is_liked,
        })
    except Exception as e:
        print(f"Error in dish_detail: {e}")
        raise Http404("Блюдо не найдено")

@login_required
@require_POST
def toggle_like_dish(request, dish_id):
    """Добавить/удалить блюдо из избранного"""
    try:
        dish = get_object_or_404(Dish, id=dish_id)
        user_profile = get_user_profile(request.user)

        if dish in user_profile.liked_dishes.all():
            user_profile.liked_dishes.remove(dish)
            liked = False
            message = f'Блюдо "{dish.name}" удалено из избранного'
        else:
            user_profile.liked_dishes.add(dish)
            liked = True
            message = f'Блюдо "{dish.name}" добавлено в избранное'

        return JsonResponse({
            'success': True,
            'liked': liked,
            'message': message,
            'likes_count': user_profile.liked_dishes.count()
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def update_daily_menu(request):
    if request.method == 'POST':
        day = request.POST.get('day')
        meal_type = request.POST.get('meal_type')
        dish_id = request.POST.get('dish_id')

        try:
            menu_date = date(int(request.POST.get('year')), int(request.POST.get('month')), int(day))
            daily_menu, created = DailyMenu.objects.get_or_create(
                user=request.user,
                date=menu_date,
                defaults={meal_type: Dish.objects.get(id=dish_id) if dish_id else None}
            )

            if not created:
                if dish_id:
                    setattr(daily_menu, meal_type, Dish.objects.get(id=dish_id))
                else:
                    setattr(daily_menu, meal_type, None)
                daily_menu.save()

            return JsonResponse({'success': True, 'message': 'Меню обновлено'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Неверный метод запроса'})


@login_required
def get_daily_menu(request):
    day = request.GET.get('day')
    year = request.GET.get('year')
    month = request.GET.get('month')

    try:
        menu_date = date(int(year), int(month), int(day))
        daily_menu = DailyMenu.objects.filter(
            user=request.user,
            date=menu_date
        ).first()

        if daily_menu:
            data = {
                'breakfast': {
                    'id': daily_menu.breakfast.id if daily_menu.breakfast else None,
                    'name': daily_menu.breakfast.name if daily_menu.breakfast else None
                } if daily_menu.breakfast else None,
                'lunch': {
                    'id': daily_menu.lunch.id if daily_menu.lunch else None,
                    'name': daily_menu.lunch.name if daily_menu.lunch else None
                } if daily_menu.lunch else None,
                'dinner': {
                    'id': daily_menu.dinner.id if daily_menu.dinner else None,
                    'name': daily_menu.dinner.name if daily_menu.dinner else None
                } if daily_menu.dinner else None,
            }
        else:
            data = {}

        return JsonResponse({'success': True, 'menu': data})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# УДАЛЕНО: generate_shopping_list - больше не генерируем список покупок из меню

def custom_404(request, exception):
    """Кастомный обработчик 404 ошибки"""
    return render(request, 'app/404.html', status=404)


def custom_500(request):
    """Кастомный обработчик 500 ошибки"""
    return render(request, 'app/500.html', status=500)


@login_required
def shopping_list(request):
    """Страница списка покупок"""
    items = ShoppingListItem.objects.filter(user=request.user)

    # Получаем избранные блюда для авторизованного пользователя
    liked_dishes_ids = []
    if request.user.is_authenticated:
        user_profile = get_user_profile(request.user)
        liked_dishes_ids = list(user_profile.liked_dishes.values_list('id', flat=True))

    context = {
        'items': items,
        'liked_dishes_ids': liked_dishes_ids,
    }
    return render(request, 'app/shopping_list.html', context)

@login_required
@require_POST
def add_to_shopping_list(request):
    """Добавление ингредиента в список покупок"""
    name = request.POST.get('name', '').strip()
    quantity = request.POST.get('quantity', '').strip()

    if not name:
        return JsonResponse({'success': False, 'error': 'Название ингредиента не может быть пустым'})

    try:
        # Проверяем, нет ли уже такого ингредиента в списке
        existing_item = ShoppingListItem.objects.filter(
            user=request.user,
            name=name,
            completed=False
        ).first()

        if existing_item:
            return JsonResponse({
                'success': False,
                'error': 'Этот ингредиент уже есть в списке покупок'
            })

        item = ShoppingListItem.objects.create(
            user=request.user,
            name=name,
            quantity=quantity
        )

        return JsonResponse({
            'success': True,
            'message': 'Ингредиент добавлен в список покупок',
            'item_id': item.id,
            'item_name': item.name
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def add_dish_ingredients_to_shopping_list(request, dish_id):
    """Добавление всех ингредиентов блюда в список покупок"""
    try:
        dish = get_object_or_404(Dish, id=dish_id)
        ingredients = dish.get_ingredients_list()

        added_count = 0
        skipped_count = 0

        for ingredient in ingredients:
            if ingredient.strip():
                # Проверяем, нет ли уже такого ингредиента
                existing_item = ShoppingListItem.objects.filter(
                    user=request.user,
                    name=ingredient.strip(),
                    completed=False
                ).first()

                if not existing_item:
                    ShoppingListItem.objects.create(
                        user=request.user,
                        name=ingredient.strip()
                    )
                    added_count += 1
                else:
                    skipped_count += 1

        message = f'Добавлено {added_count} ингредиентов в список покупок'
        if skipped_count > 0:
            message += f' ({skipped_count} уже были в списке)'

        return JsonResponse({
            'success': True,
            'message': message,
            'added_count': added_count,
            'skipped_count': skipped_count
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# НОВАЯ ФУНКЦИЯ: Добавление отдельного ингредиента в список покупок
@login_required
@require_POST
def add_single_ingredient_to_shopping_list(request):
    """Добавление одного ингредиента в список покупок"""
    ingredient_name = request.POST.get('ingredient_name', '').strip()

    if not ingredient_name:
        return JsonResponse({'success': False, 'error': 'Название ингредиента не может быть пустым'})

    try:
        # Проверяем, нет ли уже такого ингредиента в списке
        existing_item = ShoppingListItem.objects.filter(
            user=request.user,
            name=ingredient_name,
            completed=False
        ).first()

        if existing_item:
            return JsonResponse({
                'success': False,
                'error': 'Этот ингредиент уже есть в списке покупок'
            })

        item = ShoppingListItem.objects.create(
            user=request.user,
            name=ingredient_name
        )

        return JsonResponse({
            'success': True,
            'message': f'Ингредиент "{ingredient_name}" добавлен в список покупок',
            'item_id': item.id,
            'item_name': item.name
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def toggle_shopping_item(request):
    """Отметить ингредиент как выполненный/невыполненный"""
    item_id = request.POST.get('item_id')

    try:
        item = get_object_or_404(ShoppingListItem, id=item_id, user=request.user)
        item.completed = not item.completed
        item.save()

        status = "выполнено" if item.completed else "не выполнено"
        return JsonResponse({
            'success': True,
            'message': f'Ингредиент отмечен как {status}',
            'completed': item.completed
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def remove_shopping_item(request):
    """Удаление ингредиента из списка покупок"""
    item_id = request.POST.get('item_id')

    try:
        item = get_object_or_404(ShoppingListItem, id=item_id, user=request.user)
        item.delete()

        return JsonResponse({'success': True, 'message': 'Ингредиент удален из списка покупок'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
@require_POST
def clear_shopping_list(request):
    try:
        ShoppingListItem.objects.filter(user=request.user).delete()
        return JsonResponse({'success': True, 'message': 'Список покупок очищен'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})