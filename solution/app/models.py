from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class Cuisine(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название кухни")
    description = models.TextField(verbose_name="Описание", blank=True)
    image = models.ImageField(upload_to='cuisines/', blank=True, null=True, verbose_name="Изображение")

    class Meta:
        verbose_name = "Кухня"
        verbose_name_plural = "Кухни"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('cuisine_detail', kwargs={'cuisine_id': self.id})


class Dish(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Легко'),
        ('medium', 'Средне'),
        ('hard', 'Сложно'),
    ]

    name = models.CharField(max_length=200, verbose_name="Название блюда")
    cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE, verbose_name="Кухня", related_name='dishes')
    description = models.TextField(verbose_name="Описание")
    ingredients = models.TextField(verbose_name="Ингредиенты")
    recipe = models.TextField(verbose_name="Рецепт", blank=True, null=True)
    cooking_time = models.IntegerField(help_text="Время в минутах", verbose_name="Время приготовления")
    difficulty = models.CharField(
        max_length=50,
        choices=DIFFICULTY_CHOICES,
        verbose_name="Сложность",
        default='medium'
    )
    calories = models.IntegerField(default=0, help_text="Калории на порцию", verbose_name="Калории")
    image = models.ImageField(upload_to='dishes/', blank=True, null=True, verbose_name="Изображение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Блюдо"
        verbose_name_plural = "Блюда"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['cuisine']),
            models.Index(fields=['difficulty']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dish_detail', kwargs={'dish_id': self.id})

    def get_ingredients_list(self):
        """Преобразует текстовые ингредиенты в список"""
        return [ingredient.strip() for ingredient in self.ingredients.split(',') if ingredient.strip()]

    @property
    def ingredients_list(self):
        """Свойство для доступа к списку ингредиентов в шаблонах"""
        return self.get_ingredients_list()

    def get_difficulty_display_name(self):
        """Возвращает читаемое название сложности"""
        difficulty_dict = dict(self.DIFFICULTY_CHOICES)
        return difficulty_dict.get(self.difficulty, self.difficulty)

    def get_ingredients_count(self):
        """Возвращает количество ингредиентов"""
        return len(self.get_ingredients_list())


class DailyMenu(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Завтрак'),
        ('lunch', 'Обед'),
        ('dinner', 'Ужин'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    date = models.DateField(verbose_name="Дата")
    breakfast = models.ForeignKey(
        'Dish',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='breakfast_menus',
        verbose_name="Завтрак"
    )
    lunch = models.ForeignKey(
        'Dish',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lunch_menus',
        verbose_name="Обед"
    )
    dinner = models.ForeignKey(
        'Dish',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dinner_menus',
        verbose_name="Ужин"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Дневное меню"
        verbose_name_plural = "Дневные меню"
        unique_together = ['user', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.date}"

    def get_total_calories(self):
        """Возвращает общее количество калорий за день"""
        total = 0
        if self.breakfast:
            total += self.breakfast.calories
        if self.lunch:
            total += self.lunch.calories
        if self.dinner:
            total += self.dinner.calories
        return total


class ShoppingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    ingredient = models.CharField(max_length=200, verbose_name="Ингредиент")
    quantity = models.CharField(max_length=50, blank=True, verbose_name="Количество")
    completed = models.BooleanField(default=False, verbose_name="Выполнено")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
        ordering = ['completed', 'created_at']

    def __str__(self):
        return f"{self.ingredient} - {self.user.username}"


class FridgeItem(models.Model):
    CATEGORY_CHOICES = [
        ('vegetables', 'Овощи'),
        ('fruits', 'Фрукты'),
        ('meat', 'Мясо'),
        ('fish', 'Рыба'),
        ('dairy', 'Молочные продукты'),
        ('grains', 'Крупы и злаки'),
        ('spices', 'Специи и приправы'),
        ('beverages', 'Напитки'),
        ('other', 'Другое'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    name = models.CharField(max_length=200, verbose_name="Название продукта")
    category = models.CharField(
        max_length=100,
        choices=CATEGORY_CHOICES,
        default='other',
        verbose_name="Категория"
    )
    quantity = models.CharField(max_length=100, blank=True, verbose_name="Количество")
    added_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    expiry_date = models.DateField(null=True, blank=True, verbose_name="Срок годности")
    notes = models.TextField(blank=True, verbose_name="Заметки")

    class Meta:
        verbose_name = "Продукт в холодильнике"
        verbose_name_plural = "Продукты в холодильнике"
        ordering = ['category', 'added_date']
        indexes = [
            models.Index(fields=['user', 'category']),
        ]

    def __str__(self):
        return f"{self.name} - {self.user.username}"

    def is_expired(self):
        """Проверяет, истек ли срок годности"""
        if self.expiry_date:
            return self.expiry_date < timezone.now().date()
        return False

    def days_until_expiry(self):
        """Возвращает количество дней до истечения срока годности"""
        if self.expiry_date:
            today = timezone.now().date()
            delta = (self.expiry_date - today).days
            return max(delta, 0) if delta >= 0 else delta
        return None

    def get_expiry_status(self):
        """Возвращает статус срока годности"""
        if not self.expiry_date:
            return 'no_date'
        days = self.days_until_expiry()
        if days is None:
            return 'no_date'
        if days < 0:
            return 'expired'
        elif days <= 3:
            return 'critical'
        elif days <= 7:
            return 'warning'
        else:
            return 'good'


class UserPreference(models.Model):
    """Модель для хранения предпочтений пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Пользователь")
    daily_calorie_goal = models.IntegerField(default=2000, verbose_name="Дневная норма калорий")
    preferred_cuisines = models.ManyToManyField(Cuisine, blank=True, verbose_name="Предпочтительные кухни")
    allergies = models.TextField(blank=True, verbose_name="Аллергии")
    dietary_restrictions = models.TextField(blank=True, verbose_name="Диетические ограничения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Предпочтение пользователя"
        verbose_name_plural = "Предпочтения пользователей"

    def __str__(self):
        return f"Предпочтения {self.user.username}"


class ShoppingListItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    quantity = models.CharField(max_length=100, blank=True)
    completed = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.name} - {self.user.username}"