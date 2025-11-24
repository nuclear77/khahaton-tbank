from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline для отображения профиля пользователя в админке User"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Профиль пользователя'
    filter_horizontal = ('liked_dishes',)
    fields = ('daily_calories', 'liked_dishes')
    extra = 0


class CustomUserAdmin(UserAdmin):
    """Кастомная админка для User с inline профилем"""
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'profile_info')

    def profile_info(self, obj):
        try:
            profile = obj.userprofile
            liked_count = profile.liked_dishes.count()
            return f'Калории: {profile.daily_calories}, Избранное: {liked_count}'
        except UserProfile.DoesNotExist:
            return 'Профиль не создан'

    profile_info.short_description = 'Информация профиля'


class UserProfileAdmin(admin.ModelAdmin):
    """Админка для модели UserProfile"""
    list_display = ('user', 'daily_calories', 'liked_dishes_count', 'user_date_joined')
    list_filter = ('daily_calories',)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    filter_horizontal = ('liked_dishes',)
    readonly_fields = ('user_date_joined_display',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'daily_calories')
        }),
        ('Избранные блюда', {
            'fields': ('liked_dishes',)
        }),
        ('Дополнительная информация', {
            'fields': ('user_date_joined_display',),
            'classes': ('collapse',)
        }),
    )

    def liked_dishes_count(self, obj):
        return obj.liked_dishes.count()

    liked_dishes_count.short_description = 'Кол-во избранных блюд'

    def user_date_joined(self, obj):
        return obj.user.date_joined.strftime('%d.%m.%Y %H:%M')

    user_date_joined.short_description = 'Дата регистрации'

    def user_date_joined_display(self, obj):
        return obj.user.date_joined.strftime('%d.%m.%Y %H:%M:%S')

    user_date_joined_display.short_description = 'Дата регистрации пользователя'


# Перерегистрируем UserAdmin для добавления inline профиля
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Регистрируем UserProfile отдельно
admin.site.register(UserProfile, UserProfileAdmin)