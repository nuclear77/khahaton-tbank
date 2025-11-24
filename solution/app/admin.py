from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import (
    Cuisine, Dish, DailyMenu, ShoppingList,
    FridgeItem, UserPreference, ShoppingListItem
)


class CuisineAdmin(admin.ModelAdmin):
    list_display = ('name', 'dishes_count', 'image_preview')
    list_filter = ('name',)
    search_fields = ('name', 'description')
    readonly_fields = ('image_preview',)

    def dishes_count(self, obj):
        return obj.dishes.count()

    dishes_count.short_description = 'Количество блюд'

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 50px;" />'
        return "Нет изображения"

    image_preview.allow_tags = True
    image_preview.short_description = 'Превью'


class DishAdmin(admin.ModelAdmin):
    list_display = ('name', 'cuisine', 'cooking_time', 'difficulty', 'calories', 'image_preview')
    list_filter = ('cuisine', 'difficulty', 'created_at')
    search_fields = ('name', 'description', 'ingredients')
    readonly_fields = ('created_at', 'updated_at', 'image_preview', 'ingredients_list_display')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'cuisine', 'description', 'image', 'image_preview')
        }),
        ('Детали рецепта', {
            'fields': ('ingredients', 'ingredients_list_display', 'recipe', 'cooking_time', 'difficulty', 'calories')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" style="max-height: 100px; max-width: 100px;" />'
        return "Нет изображения"

    image_preview.allow_tags = True
    image_preview.short_description = 'Превью'

    def ingredients_list_display(self, obj):
        ingredients = obj.get_ingredients_list()
        return ", ".join(ingredients) if ingredients else "Нет ингредиентов"

    ingredients_list_display.short_description = 'Список ингредиентов (авто)'


class DailyMenuAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'breakfast', 'lunch', 'dinner', 'total_calories')
    list_filter = ('date', 'user', 'created_at')
    search_fields = ('user__username', 'breakfast__name', 'lunch__name', 'dinner__name')
    readonly_fields = ('created_at', 'updated_at', 'total_calories')
    date_hierarchy = 'date'

    def total_calories(self, obj):
        return obj.get_total_calories()

    total_calories.short_description = 'Общие калории'


class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('user', 'ingredient', 'quantity', 'completed', 'created_at')
    list_filter = ('completed', 'created_at', 'user')
    search_fields = ('ingredient', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('completed',)


class FridgeItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'category', 'quantity', 'expiry_status', 'added_date')
    list_filter = ('category', 'added_date', 'user')
    search_fields = ('name', 'user__username', 'notes')
    readonly_fields = ('added_date', 'expiry_status_display')
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'name', 'category', 'quantity')
        }),
        ('Дополнительная информация', {
            'fields': ('expiry_date', 'expiry_status_display', 'notes')
        }),
        ('Даты', {
            'fields': ('added_date',),
            'classes': ('collapse',)
        }),
    )

    def expiry_status_display(self, obj):
        status = obj.get_expiry_status()
        status_map = {
            'no_date': 'Без срока',
            'expired': 'Просрочено',
            'critical': 'Критический (<= 3 дней)',
            'warning': 'Предупреждение (<= 7 дней)',
            'good': 'Хороший'
        }
        return status_map.get(status, status)

    expiry_status_display.short_description = 'Статус срока годности'

    def expiry_status(self, obj):
        status = obj.get_expiry_status()
        if status == 'expired':
            return '❌ Просрочено'
        elif status == 'critical':
            return '🔴 Критический'
        elif status == 'warning':
            return '🟡 Предупреждение'
        elif status == 'good':
            return '🟢 Хороший'
        else:
            return '⚪ Без срока'

    expiry_status.short_description = 'Статус'


class UserPreferenceInline(admin.StackedInline):
    model = UserPreference
    can_delete = False
    verbose_name_plural = 'Предпочтения пользователя'
    filter_horizontal = ('preferred_cuisines',)
    fieldsets = (
        ('Основные настройки', {
            'fields': ('daily_calorie_goal', 'preferred_cuisines')
        }),
        ('Ограничения', {
            'fields': ('allergies', 'dietary_restrictions'),
            'classes': ('collapse',)
        }),
    )


class CustomUserAdmin(UserAdmin):
    inlines = (UserPreferenceInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'preferences_info')

    def preferences_info(self, obj):
        try:
            pref = obj.userpreference
            return f'Калории: {pref.daily_calorie_goal}'
        except UserPreference.DoesNotExist:
            return 'Не настроено'

    preferences_info.short_description = 'Настройки питания'


class ShoppingListItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'quantity', 'completed', 'added_at')
    list_filter = ('completed', 'added_at', 'user')
    search_fields = ('name', 'user__username')
    readonly_fields = ('added_at',)
    list_editable = ('completed', 'quantity')


# Регистрация моделей в админке
admin.site.register(Cuisine, CuisineAdmin)
admin.site.register(Dish, DishAdmin)
admin.site.register(DailyMenu, DailyMenuAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(FridgeItem, FridgeItemAdmin)
admin.site.register(ShoppingListItem, ShoppingListItemAdmin)

# Перерегистрируем UserAdmin для добавления inline
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# Регистрируем UserPreference отдельно (опционально)
@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'daily_calorie_goal', 'allergies_short', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'allergies', 'dietary_restrictions')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('preferred_cuisines',)

    def allergies_short(self, obj):
        return obj.allergies[:50] + '...' if len(obj.allergies) > 50 else obj.allergies

    allergies_short.short_description = 'Аллергии (кратко)'