function toggleShoppingItem(itemId) {
        fetch("{% url 'toggle_shopping_item' %}", {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `item_id=${itemId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const itemElement = document.getElementById(`item-${itemId}`);
                if (data.completed) {
                    itemElement.classList.add('completed');
                } else {
                    itemElement.classList.remove('completed');
                }
                // Обновляем кнопку
                const button = itemElement.querySelector('.btn-group .btn:first-child');
                button.textContent = data.completed ? '↶' : '✓';
                button.className = data.completed ?
                    'btn btn-sm btn-warning' : 'btn btn-sm btn-success';
            } else {
                alert('Ошибка: ' + data.error);
            }
        });
    }

    function removeShoppingItem(itemId) {
        if (!confirm('Удалить ингредиент из списка?')) return;

        fetch("{% url 'remove_shopping_item' %}", {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `item_id=${itemId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById(`item-${itemId}`).remove();
                // Если список пуст, показываем empty state
                if (document.querySelectorAll('.shopping-item').length === 0) {
                    location.reload();
                }
            } else {
                alert('Ошибка: ' + data.error);
            }
        });
    }

    function clearShoppingList() {
        if (!confirm('Очистить весь список покупок?')) return;

        fetch("{% url 'clear_shopping_list' %}", {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Ошибка: ' + data.error);
            }
        });
    }

    function getCSRFToken() {
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1];
        return cookieValue || '';
    }