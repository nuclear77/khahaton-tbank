 document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('searchCuisine');
        const sortSelect = document.getElementById('sortCuisine');
        const cuisineCards = document.querySelectorAll('.cuisine-card');

        // Функция для поиска кухонь
        function filterCuisines() {
            const searchTerm = searchInput.value.toLowerCase();

            cuisineCards.forEach(card => {
                const cuisineName = card.querySelector('.cuisine-name').textContent.toLowerCase();
                if (cuisineName.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        // Функция для сортировки кухонь
        function sortCuisines() {
            const sortValue = sortSelect.value;
            const container = document.getElementById('cuisines-container');
            const cards = Array.from(cuisineCards);

            cards.sort((a, b) => {
                const nameA = a.querySelector('.cuisine-name').textContent;
                const nameB = b.querySelector('.cuisine-name').textContent;

                switch(sortValue) {
                    case 'name':
                        return nameA.localeCompare(nameB);
                    case 'name_desc':
                        return nameB.localeCompare(nameA);
                    case 'dishes_count':
                        const countA = parseInt(a.querySelector('.cuisine-info span').textContent.match(/\d+/)[0]);
                        const countB = parseInt(b.querySelector('.cuisine-info span').textContent.match(/\d+/)[0]);
                        return countB - countA;
                    default:
                        return 0;
                }
            });

            // Очищаем контейнер и добавляем отсортированные карточки
            container.innerHTML = '';
            cards.forEach(card => {
                container.appendChild(card);
            });
        }

        // Обработчики событий
        searchInput.addEventListener('input', filterCuisines);
        sortSelect.addEventListener('change', sortCuisines);

        // Инициализация
        filterCuisines();
    });