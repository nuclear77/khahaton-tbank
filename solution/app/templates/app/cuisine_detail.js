document.addEventListener('DOMContentLoaded', function() {
        // Обработчик для кнопок лайка
        document.addEventListener('click', async function(e) {
            if (e.target.closest('.like-btn') && !e.target.closest('.like-btn').disabled) {
                e.preventDefault();
                e.stopPropagation();

                const likeBtn = e.target.closest('.like-btn');
                const dishId = likeBtn.getAttribute('data-dish-id');

                try {
                    const response = await fetch(`/dish/${dishId}/toggle_like/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCSRFToken(),
                            'Content-Type': 'application/json',
                        },
                    });

                    const data = await response.json();

                    if (data.success) {
                        const heartIcon = likeBtn.querySelector('.heart-icon');
                        if (data.liked) {
                            likeBtn.classList.add('liked');
                            heartIcon.textContent = '♥';
                            // Анимация
                            likeBtn.style.transform = 'scale(1.2)';
                            setTimeout(() => {
                                likeBtn.style.transform = 'scale(1)';
                            }, 300);
                        } else {
                            likeBtn.classList.remove('liked');
                            heartIcon.textContent = '♡';
                        }
                    } else {
                        alert('Ошибка: ' + data.error);
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Произошла ошибка при добавлении в избранное');
                }
            }
        });

        // Функция для получения CSRF токена
        function getCSRFToken() {
            const cookieValue = document.cookie
                .split('; ')
                .find(row => row.startsWith('csrftoken='))
                ?.split('=')[1];
            return cookieValue || '';
        }
    });