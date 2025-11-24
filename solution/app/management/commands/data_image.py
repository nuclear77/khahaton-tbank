import requests
from django.core.files import File
from django.core.management.base import BaseCommand
from django.apps import apps
import time
from io import BytesIO


class Command(BaseCommand):
    help = 'Добавляет картинки блюдам и флаги кухням'

    def handle(self, *args, **options):
        self.stdout.write('Добавляем картинки и флаги...')

        # Получаем модели через apps.get_model
        # ЗАМЕНИ 'app' на имя твоего приложения!
        Dish = apps.get_model('app', 'Dish')
        Cuisine = apps.get_model('app', 'Cuisine')

        # Сначала добавляем флаги кухням
        self.add_cuisine_flags(Cuisine)

        # Затем добавляем картинки блюдам
        self.add_dish_images(Dish)

        self.stdout.write(self.style.SUCCESS('✅ Все картинки и флаги добавлены!'))

    def add_cuisine_flags(self, Cuisine):
        """Добавляет флаги для кухонь"""
        cuisine_flags = {
            'Итальянская': 'https://flagcdn.com/w320/it.png',
            'Французская': 'https://flagcdn.com/w320/fr.png',
            'Немецкая': 'https://flagcdn.com/w320/de.png',
            'Еврейская': 'https://flagcdn.com/w320/il.png',
            'Русская': 'https://flagcdn.com/w320/ru.png',
            'Украинская': 'https://flagcdn.com/w320/ua.png',
            'Английская': 'https://flagcdn.com/w320/gb.png',
            'Мексиканская': 'https://flagcdn.com/w320/mx.png',
            'Индийская': 'https://flagcdn.com/w320/in.png',
            'Тайская': 'https://flagcdn.com/w320/th.png',
            'Испанская': 'https://flagcdn.com/w320/es.png',
            'Греческая': 'https://flagcdn.com/w320/gr.png',
        }

        for cuisine_name, flag_url in cuisine_flags.items():
            try:
                cuisine = Cuisine.objects.filter(name=cuisine_name).first()
                if cuisine and not cuisine.image:
                    if self.download_image(cuisine, flag_url, is_flag=True):
                        self.stdout.write(f'✅ Флаг добавлен для: {cuisine_name}')
                    else:
                        self.stdout.write(f'⚠️ Не удалось загрузить флаг для: {cuisine_name}')
                else:
                    self.stdout.write(f'ℹ️ Кухня уже имеет флаг или не найдена: {cuisine_name}')
                time.sleep(0.5)  # Увеличиваем задержку
            except Exception as e:
                self.stdout.write(f'❌ Ошибка для кухни {cuisine_name}: {str(e)}')

    def add_dish_images(self, Dish):
        """Добавляет картинки для блюд"""
        dish_images = {
            # Итальянская кухня
            'Паста Карбонара': 'https://images.unsplash.com/photo-1621996346565-e3dbc353d2e5?w=800&fit=crop',
            'Пицца Маргарита': 'https://images.unsplash.com/photo-1604068549290-dea0e4a305ca?w=800&fit=crop',
            'Ризотто': 'https://images.unsplash.com/photo-1476124369491-e7addf5db371?w=800&fit=crop',
            'Тирамису': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=800&fit=crop',

            # Французская кухня
            'Круассан': 'https://images.unsplash.com/photo-1555507032-7d78da6f1b13?w=800&fit=crop',
            'Рататуй': 'https://images.unsplash.com/photo-1572453800999-e8d2d1589b7c?w=800&fit=crop',
            'Киш Лорен': 'https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800&fit=crop',
            'Крем-брюле': 'https://images.unsplash.com/photo-1551024506-0bccd828d307?w=800&fit=crop',

            # Немецкая кухня
            'Берлинер': 'https://images.unsplash.com/photo-1551106652-a5bcf4b29ab6?w=800&fit=crop',

            # Еврейская кухня
            'Фаршмак из говядины': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&fit=crop',

            # Русская/Украинская кухня
            'Суп гороховый': 'https://images.unsplash.com/photo-1546549032-9571cd6b27df?w=800&fit=crop',
            'Борщ': 'https://images.unsplash.com/photo-1546793665-c74683f339c1?w=800&fit=crop',
            'Пельмени': 'https://images.unsplash.com/photo-1589100026303-57d6b6274fbe?w=800&fit=crop',
            'Блины': 'https://images.unsplash.com/photo-1551789607-c1aa0d1f73c9?w=800&fit=crop',
            'Оливье': 'https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=800&fit=crop',

            # Английская кухня
            'Говядина Веллингтон': 'https://images.unsplash.com/photo-1589302168068-964664d93dc0?w=800&fit=crop',
            'Английские мафины': 'https://images.unsplash.com/photo-1555507032-7d78da6f1b13?w=800&fit=crop',
            'Яйца Скотч': 'https://images.unsplash.com/photo-1562967916-eb82221dfb92?w=800&fit=crop',
            'Пирог с бараниной': 'https://images.unsplash.com/photo-1608190003443-86ab6f120a6c?w=800&fit=crop',

            # Мексиканская кухня
            'Тако': 'https://images.unsplash.com/photo-1565299585323-38174bb13f3d?w=800&fit=crop',
            'Буррито': 'https://images.unsplash.com/photo-1519183073328-330cc6ead67e?w=800&fit=crop',
            'Кесадилья': 'https://images.unsplash.com/photo-1615870216519-2f9fa575fa5c?w=800&fit=crop',
            'Гуакамоле': 'https://images.unsplash.com/photo-1534308983496-4fabb1a015ee?w=800&fit=crop',

            # Индийская кухня
            'Карри': 'https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=800&fit=crop',
            'Тикка Масала': 'https://images.unsplash.com/photo-1565557623262-b51c2513a641?w=800&fit=crop',
            'Бириани': 'https://images.unsplash.com/photo-1563379091339-03246963d96c?w=800&fit=crop',
            'Самоса': 'https://images.unsplash.com/photo-1601050690597-df0568f70946?w=800&fit=crop',

            # Тайская кухня
            'Том Ям': 'https://images.unsplash.com/photo-1552465011-b4e30bf7349d?w=800&fit=crop',
            'Пад Тай': 'https://images.unsplash.com/photo-1559314809-0f155186aed0?w=800&fit=crop',
            'Зеленое карри': 'https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=800&fit=crop',
            'Клейкий рис с манго': 'https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&fit=crop',

            # Испанская кухня
            'Паэлья': 'https://images.unsplash.com/photo-1569050467449-8b6e68b9c6ec?w=800&fit=crop',

            # Греческая кухня
            'Греческий салат': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=800&fit=crop',
        }

        for dish_name, image_url in dish_images.items():
            try:
                dish = Dish.objects.filter(name=dish_name).first()
                if dish and not dish.image:
                    if self.download_image(dish, image_url):
                        self.stdout.write(f'✅ Картинка добавлена для: {dish_name}')
                    else:
                        self.stdout.write(f'⚠️ Не удалось загрузить картинку для: {dish_name}')
                else:
                    self.stdout.write(f'ℹ️ Блюдо уже имеет картинку или не найдено: {dish_name}')
                time.sleep(0.5)  # Увеличиваем задержку
            except Exception as e:
                self.stdout.write(f'❌ Ошибка для блюда {dish_name}: {str(e)}')

    def download_image(self, obj, image_url, is_flag=False):
        """Скачивает и сохраняет изображение используя BytesIO (работа в памяти)"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(image_url, timeout=30, headers=headers)

            if response.status_code == 200:
                # Используем BytesIO для работы в памяти
                image_data = BytesIO(response.content)

                # Создаем имя файла
                prefix = 'flag' if is_flag else 'dish'
                clean_name = "".join(c for c in obj.name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                filename = f"{prefix}_{clean_name.replace(' ', '_').replace('/', '_')}.jpg"

                # Сохраняем изображение напрямую из памяти
                obj.image.save(filename, File(image_data), save=True)
                return True
            else:
                self.stdout.write(f'⚠️ HTTP ошибка {response.status_code} для {image_url}')
                return False

        except requests.exceptions.RequestException as e:
            self.stdout.write(f'⚠️ Ошибка сети при загрузке {image_url}: {str(e)}')
            return False
        except Exception as e:
            self.stdout.write(f'⚠️ Неожиданная ошибка при загрузке {image_url}: {str(e)}')
            return False