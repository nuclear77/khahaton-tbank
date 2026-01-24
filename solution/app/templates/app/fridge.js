document.addEventListener('DOMContentLoaded', function() {
        const ingredientInput = document.getElementById('ingredientInput');
        const addIngredientBtn = document.getElementById('addIngredientBtn');
        const ingredientsList = document.getElementById('ingredientsList');
        const recipesSection = document.getElementById('recipesSection');
        const loadingSpinner = document.getElementById('loadingSpinner');
        const refreshBtn = document.getElementById('refreshRecommendationsBtn');
        const quickIngredients = document.querySelectorAll('.quick-ingredient');

        // Функция для добавления ингредиента
        function addIngredient(ingredientName) {
            if (ingredientName.trim() === '') return;

            const formData = new FormData();
            formData.append('ingredient', ingredientName.trim());
            formData.append('csrfmiddlewaretoken', '{{ csrf_token }}');

            fetch('{% url "add_to_fridge" %}', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateIngredientsList();
                    ingredientInput.value = '';
                    loadRecommendations();
                } else {
                    alert('Ошибка: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при добавлении продукта');
            });
        }

        // Функция для удаления ингредиента
        function removeIngredient(itemId) {
            if (!confirm('Удалить продукт из холодильника?')) return;

            const formData = new FormData();
            formData.append('item_id', itemId);
            formData.append('csrfmiddlewaretoken', '{{ csrf_token }}');

            fetch('{% url "remove_from_fridge" %}', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateIngredientsList();
                    loadRecommendations();
                } else {
                    alert('Ошибка: ' + data.error);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Произошла ошибка при удалении продукта');
            });
        }

        // Функция для обновления списка ингредиентов
        function updateIngredientsList() {
            window.location.reload();
        }

        // Функция для загрузки рекомендаций
        function loadRecommendations() {
            loadingSpinner.style.display = 'block';
            recipesSection.style.display = 'none';

            fetch('{% url "fridge_recommendations" %}')
            .then(response => response.json())
            .then(data => {
                loadingSpinner.style.display = 'none';
                recipesSection.style.display = 'block';

                if (data.success) {
                    updateRecipesSection(data.dishes);
                } else {
                    recipesSection.innerHTML = `
                        <div class="alert alert-danger">
                            Ошибка при загрузке рекомендаций: ${data.error}
                        </div>
                    `;
                }
            })
            .catch(error => {
                loadingSpinner.style.display = 'none';
                recipesSection.style.display = 'block';
                recipesSection.innerHTML = `
                    <div class="alert alert-danger">
                        Произошла ошибка при загрузке рекомендаций
                    </div>
                `;
                console.error('Error:', error);
            });
        }

        // Функция для обновления секции с рецептами
        function updateRecipesSection(dishes) {
            if (dishes.length === 0) {
                recipesSection.innerHTML = `
                    <div class="alert alert-info">
                        По вашим продуктам не найдено подходящих рецептов. Попробуйте добавить больше продуктов.
                    </div>
                `;
                return;
            }

            let recipesHTML = `
                <div class="alert alert-info">
                    На основе ваших продуктов найдено ${dishes.length} рецептов
                </div>
                <div class="row">
            `;

            dishes.forEach(dish => {
                const imageHTML = dish.image_url ?
                    `<img src="${dish.image_url}" alt="${dish.name}" class="dish-image">` :
                    `<div class="dish-image-placeholder">${dish.name}</div>`;

                recipesHTML += `
                    <div class="col-lg-6 col-md-12 mb-4">
                        <div class="dish-card" onclick="window.location.href='/dish/${dish.id}'">
                            <div class="dish-image-container">
                                ${imageHTML}
                            </div>
                            <div class="dish-content">
                                <div class="dish-header">
                                    <h6 class="dish-title">${dish.name}</h6>
                                    <span class="match-badge">${dish.match_percentage}% совпадение</span>
                                </div>
                                <p class="dish-description">${dish.description}</p>
                                <div class="dish-meta">
                                    <span>⏱️ ${dish.cooking_time} мин</span>
                                    <span>📊 ${dish.difficulty}</span>
                                    <span>🔥 ${dish.calories} ккал</span>
                                </div>
                                <div class="dish-actions">
                                    <a href="/dish/${dish.id}" class="btn btn-sm btn-outline-light">Смотреть рецепт</a>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });

            recipesHTML += '</div>';
            recipesSection.innerHTML = recipesHTML;
        }

        // Обработчики событий
        addIngredientBtn.addEventListener('click', function() {
            addIngredient(ingredientInput.value);
        });

        ingredientInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                addIngredient(ingredientInput.value);
            }
        });

        quickIngredients.forEach(btn => {
            btn.addEventListener('click', function() {
                const ingredient = this.getAttribute('data-ingredient');
                addIngredient(ingredient);
            });
        });

        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('remove-ingredient')) {
                const itemId = e.target.getAttribute('data-item-id');
                removeIngredient(itemId);
            }
        });

        refreshBtn.addEventListener('click', loadRecommendations);

        // Инициализация
        if (document.querySelectorAll('.ingredient-item').length === 0) {
            recipesSection.style.display = 'block';
        }
    });