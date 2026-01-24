document.addEventListener('DOMContentLoaded', function() {
        // Получаем URL из data-атрибутов
        const urls = document.getElementById('urls').dataset;

        // Добавление отдельного ингредиента в список покупок
        const addSingleButtons = document.querySelectorAll('.add-single-ingredient');
        addSingleButtons.forEach(button => {
            button.addEventListener('click', function() {
                const ingredientName = this.getAttribute('data-ingredient-name');

                fetch('{% url "add_single_ingredient_to_shopping_list" %}', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': '{{ csrf_token }}',
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        'ingredient_name': ingredientName
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                    } else {
                        alert('Ошибка: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Произошла ошибка при добавлении ингредиента');
                });
            });
        });

        // Добавление всех ингредиентов в список покупок
        const addAllButton = document.querySelector('.add-all-to-shopping-list');
        if (addAllButton) {
            addAllButton.addEventListener('click', function() {
                const dishId = this.getAttribute('data-dish-id');
                const url = urls.addToShopping.replace('0', dishId);

                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': '{{ csrf_token }}',
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                    } else {
                        alert('Ошибка: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Произошла ошибка при добавлении ингредиентов');
                });
            });
        }

        // Добавление в холодильник
        const addToFridgeButton = document.querySelector('.add-to-fridge');
        if (addToFridgeButton) {
            addToFridgeButton.addEventListener('click', function() {
                const dishId = this.getAttribute('data-dish-id');
                const url = urls.addToFridge.replace('0', dishId);

                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': '{{ csrf_token }}',
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                    } else {
                        alert('Ошибка: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Произошла ошибка при добавлении в холодильник');
                });
            });
        }

        // Избранное
        const favoriteButton = document.querySelector('.favorite-btn');
        if (favoriteButton) {
            favoriteButton.addEventListener('click', function() {
                const dishId = this.getAttribute('data-dish-id');
                const url = urls.toggleLike.replace('0', dishId);

                fetch(url, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': '{{ csrf_token }}',
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (data.liked) {
                            favoriteButton.innerHTML = '❤️ В избранном';
                            favoriteButton.classList.remove('btn-outline-danger');
                            favoriteButton.classList.add('btn-danger');
                        } else {
                            favoriteButton.innerHTML = '🤍 В избранное';
                            favoriteButton.classList.remove('btn-danger');
                            favoriteButton.classList.add('btn-outline-danger');
                        }
                    } else {
                        alert('Ошибка: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('Произошла ошибка');
                });
            });
        }
    });