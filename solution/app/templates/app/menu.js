document.addEventListener('DOMContentLoaded', function() {
        // Элементы DOM
        const calendarGrid = document.getElementById('calendar-grid');
        const dayInfo = document.getElementById('day-info');
        const selectedDayElement = document.getElementById('selected-day');
        const closeButton = document.getElementById('close-day-info');
        const saveMenuButton = document.getElementById('save-menu');
        const prevMonthBtn = document.getElementById('prev-month');
        const nextMonthBtn = document.getElementById('next-month');
        const currentMonthElement = document.getElementById('current-month');

        // Текущая дата
        let currentYear = parseInt(currentMonthElement.dataset.year);
        let currentMonth = parseInt(currentMonthElement.dataset.month);

        // Инициализация календаря
        function initCalendar() {
            generateCalendar(currentYear, currentMonth);
            updateMonthDisplay();
        }

        // Генерация календаря
        function generateCalendar(year, month) {
            calendarGrid.innerHTML = '';

            // Получаем первый день месяца и количество дней
            const firstDay = new Date(year, month - 1, 1).getDay();
            const daysInMonth = new Date(year, month, 0).getDate();

            // Добавляем пустые ячейки для дней предыдущего месяца
            for (let i = 0; i < firstDay; i++) {
                const emptyDay = document.createElement('div');
                emptyDay.className = 'calendar-day empty';
                calendarGrid.appendChild(emptyDay);
            }

            // Добавляем дни текущего месяца
            for (let i = 1; i <= daysInMonth; i++) {
                const dayElement = document.createElement('div');
                dayElement.className = 'calendar-day';
                dayElement.innerHTML = `
                    <div class="day-number">${i}</div>
                    <div class="meal-indicators">
                        <div class="meal-dot breakfast-dot" data-meal="breakfast"></div>
                        <div class="meal-dot lunch-dot" data-meal="lunch"></div>
                        <div class="meal-dot dinner-dot" data-meal="dinner"></div>
                    </div>
                `;
                dayElement.setAttribute('data-day', i);

                // Обработчик клика по дню
                dayElement.addEventListener('click', function() {
                    selectDay(this);
                });

                calendarGrid.appendChild(dayElement);
            }

            // Загружаем данные меню для этого месяца
            loadMonthMenu(year, month);
        }

        // Выбор дня
        function selectDay(dayElement) {
            // Убираем активный класс у всех дней
            document.querySelectorAll('.calendar-day').forEach(day => {
                day.classList.remove('active');
            });

            // Добавляем активный класс к выбранному дню
            dayElement.classList.add('active');

            // Показываем блок информации о дне
            const dayNumber = dayElement.getAttribute('data-day');
            selectedDayElement.textContent = dayNumber;

            // Загружаем меню для выбранного дня
            loadDayMenu(dayNumber);

            // Показываем блок информации
            dayInfo.classList.add('active');
        }

        // Загрузка меню для дня
        function loadDayMenu(day) {
            fetch(`{% url 'get_daily_menu' %}?day=${day}&year=${currentYear}&month=${currentMonth}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const menu = data.menu;

                        // Заполняем селекты и обновляем изображения
                        updateMealSelection('breakfast', menu.breakfast);
                        updateMealSelection('lunch', menu.lunch);
                        updateMealSelection('dinner', menu.dinner);

                        // Обновляем индикаторы на календаре
                        updateDayIndicators(day, menu);
                    }
                })
                .catch(error => {
                    console.error('Ошибка загрузки меню:', error);
                });
        }

        // Обновление выбора блюда и изображения
        function updateMealSelection(mealType, dish) {
            const select = document.getElementById(`${mealType}-select`);
            const imageContainer = document.getElementById(`${mealType}-image`);
            const infoContainer = document.getElementById(`${mealType}-info`);
            const nameElement = document.getElementById(`${mealType}-name`);
            const timeElement = document.getElementById(`${mealType}-time`);
            const difficultyElement = document.getElementById(`${mealType}-difficulty`);
            const caloriesElement = document.getElementById(`${mealType}-calories`);

            if (dish) {
                select.value = dish.id;

                // Обновляем изображение
                if (dish.image) {
                    imageContainer.innerHTML = `<img src="${dish.image}" alt="${dish.name}" class="dish-image">`;
                } else {
                    imageContainer.innerHTML = `<div class="dish-image-placeholder">${dish.name}</div>`;
                }

                // Показываем информацию о блюде
                nameElement.textContent = dish.name;
                timeElement.textContent = dish.cooking_time;
                difficultyElement.textContent = dish.difficulty;
                caloriesElement.textContent = dish.calories;
                infoContainer.style.display = 'block';
            } else {
                select.value = '';
                imageContainer.innerHTML = '<div class="dish-image-placeholder">Выберите блюдо</div>';
                infoContainer.style.display = 'none';
            }
        }

        // Загрузка меню для всего месяца
        function loadMonthMenu(year, month) {
            // Здесь можно добавить загрузку всех меню месяца
            // Пока просто сбрасываем индикаторы
            document.querySelectorAll('.calendar-day:not(.empty)').forEach(dayElement => {
                const day = dayElement.getAttribute('data-day');
                updateDayIndicators(day, {});
            });
        }

        // Обновление индикаторов на календаре
        function updateDayIndicators(day, menu) {
            const dayElement = document.querySelector(`.calendar-day[data-day="${day}"]`);
            if (dayElement) {
                const indicators = dayElement.querySelectorAll('.meal-dot');

                indicators.forEach(indicator => {
                    const mealType = indicator.getAttribute('data-meal');
                    if (menu[mealType]) {
                        indicator.style.opacity = '1';
                    } else {
                        indicator.style.opacity = '0.3';
                    }
                });
            }
        }

        // Сохранение меню
        saveMenuButton.addEventListener('click', function() {
            const day = selectedDayElement.textContent;
            const breakfast = document.getElementById('breakfast-select').value;
            const lunch = document.getElementById('lunch-select').value;
            const dinner = document.getElementById('dinner-select').value;

            const formData = new FormData();
            formData.append('day', day);
            formData.append('year', currentYear);
            formData.append('month', currentMonth);
            formData.append('meal_type', 'breakfast');
            formData.append('dish_id', breakfast);

            // Сохраняем завтрак
            fetch('{% url 'update_daily_menu' %}', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Сохраняем обед
                    formData.set('meal_type', 'lunch');
                    formData.set('dish_id', lunch);
                    return fetch('{% url 'update_daily_menu' %}', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Сохраняем ужин
                    formData.set('meal_type', 'dinner');
                    formData.set('dish_id', dinner);
                    return fetch('{% url 'update_daily_menu' %}', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Меню успешно сохранено!');
                    loadDayMenu(day); // Обновляем индикаторы
                }
            })
            .catch(error => {
                console.error('Ошибка сохранения меню:', error);
                alert('Ошибка при сохранении меню');
            });
        });

        // Навигация по месяцам
        prevMonthBtn.addEventListener('click', function() {
            currentMonth--;
            if (currentMonth < 1) {
                currentMonth = 12;
                currentYear--;
            }
            initCalendar();
        });

        nextMonthBtn.addEventListener('click', function() {
            currentMonth++;
            if (currentMonth > 12) {
                currentMonth = 1;
                currentYear++;
            }
            initCalendar();
        });

        // Обновление отображения месяца
        function updateMonthDisplay() {
            const monthNames = [
                'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
            ];
            currentMonthElement.textContent = `${monthNames[currentMonth - 1]} ${currentYear}`;
            currentMonthElement.dataset.year = currentYear;
            currentMonthElement.dataset.month = currentMonth;
        }

        // Закрытие блока информации
        closeButton.addEventListener('click', function() {
            dayInfo.classList.remove('active');
            document.querySelectorAll('.calendar-day').forEach(day => {
                day.classList.remove('active');
            });
        });

        // Обработчики изменения выбора блюд
        ['breakfast', 'lunch', 'dinner'].forEach(mealType => {
            const select = document.getElementById(`${mealType}-select`);
            const imageContainer = document.getElementById(`${mealType}-image`);
            const infoContainer = document.getElementById(`${mealType}-info`);
            const nameElement = document.getElementById(`${mealType}-name`);
            const timeElement = document.getElementById(`${mealType}-time`);
            const difficultyElement = document.getElementById(`${mealType}-difficulty`);
            const caloriesElement = document.getElementById(`${mealType}-calories`);

            select.addEventListener('change', function() {
                const selectedOption = this.options[this.selectedIndex];

                if (this.value) {
                    const imageUrl = selectedOption.getAttribute('data-image');
                    const cookingTime = selectedOption.getAttribute('data-cooking-time');
                    const difficulty = selectedOption.getAttribute('data-difficulty');
                    const calories = selectedOption.getAttribute('data-calories');
                    const dishName = selectedOption.textContent;

                    // Обновляем изображение
                    if (imageUrl) {
                        imageContainer.innerHTML = `<img src="${imageUrl}" alt="${dishName}" class="dish-image">`;
                    } else {
                        imageContainer.innerHTML = `<div class="dish-image-placeholder">${dishName}</div>`;
                    }

                    // Показываем информацию о блюде
                    nameElement.textContent = dishName;
                    timeElement.textContent = cookingTime;
                    difficultyElement.textContent = difficulty;
                    caloriesElement.textContent = calories;
                    infoContainer.style.display = 'block';
                } else {
                    imageContainer.innerHTML = '<div class="dish-image-placeholder">Выберите блюдо</div>';
                    infoContainer.style.display = 'none';
                }
            });
        });

        // Функция для получения CSRF токена
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        // Инициализация
        initCalendar();
    });