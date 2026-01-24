document.addEventListener('DOMContentLoaded', function() {
        // Обработчик для кнопок лайка
        document.querySelectorAll('.like-btn:not(:disabled)').forEach(button => {
            button.addEventListener('click', async function(e) {
                e.preventDefault();
                e.stopPropagation();

                const dishId = this.getAttribute('data-dish-id');

                try {
                    const response = await fetch(`/dish/${dishId}/toggle_like/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCSRFToken(),
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                    });

                    const data = await response.json();

                    if (data.success) {
                        const heartIcon = this.querySelector('.heart-icon');
                        if (data.liked) {
                            this.classList.add('liked');
                            heartIcon.textContent = '♥';
                            showAlert('Рецепт добавлен в избранное');
                            this.style.transform = 'scale(1.2)';
                            setTimeout(() => {
                                this.style.transform = 'scale(1)';
                            }, 300);
                        } else {
                            this.classList.remove('liked');
                            heartIcon.textContent = '♡';
                            showAlert('Рецепт удален из избранного');
                        }
                    } else {
                        showAlert('Ошибка: ' + data.error, 'danger');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    showAlert('Произошла ошибка при добавлении в избранное', 'danger');
                }
            });
        });

        function getCSRFToken() {
            const cookieValue = document.cookie
                .split('; ')
                .find(row => row.startsWith('csrftoken='))
                ?.split('=')[1];
            return cookieValue || '';
        }

        function showAlert(message, type = 'success') {
            const toast = document.getElementById('alertToast');
            const toastBody = toast.querySelector('.toast-body');

            toast.className = `alert alert-${type} alert-toast`;
            toastBody.textContent = message;
            toast.style.display = 'block';

            setTimeout(() => {
                toast.classList.add('show');
            }, 100);

            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => {
                    toast.style.display = 'none';
                }, 300);
            }, 3000);
        }

        // Закрытие уведомления
        const closeButton = document.querySelector('#alertToast .btn-close');
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                const toast = document.getElementById('alertToast');
                toast.classList.remove('show');
                setTimeout(() => {
                    toast.style.display = 'none';
                }, 300);
            });
        }
    });