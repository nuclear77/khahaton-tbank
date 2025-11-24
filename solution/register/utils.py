# register/utils.py
def get_user_initials(user):
    """Получить инициалы пользователя для аватара"""
    if user.first_name and user.last_name:
        return f"{user.first_name[0]}{user.last_name[0]}".upper()
    elif user.first_name:
        return user.first_name[0].upper()
    else:
        return user.username[0].upper()