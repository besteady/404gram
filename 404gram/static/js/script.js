// static/js/script.js

// Функция для перехода к профилю пользователя
function goToProfile(event) {
    event.preventDefault(); // Предотвращаем стандартную отправку формы
    const usernameInput = document.getElementById('profileSearch');
    const username = usernameInput.value.trim();
    if (username) {
        window.location.href = `/profile/${encodeURIComponent(username)}`;
    } else {
        alert("Впиши юзернейм");
    }
}

// Обработка формы создания поста
const postForm = document.getElementById('post-form');
const postStatus = document.getElementById('post-status');

if (postForm) {
    postForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Предотвращаем стандартную отправку формы

        const formData = new FormData(postForm);
        const username = formData.get('username');
        const textContent = formData.get('text_content');
        const imageFile = formData.get('image');

        if (!username) {
            setStatusMessage("Впиши юзернейм.", true);
            return;
        }
        // Проверка, что есть хотя бы текст или изображение
        if (!textContent && (!imageFile || imageFile.size === 0)) {
             setStatusMessage("Добавь текст или иозбражение.", true);
             return;
        }

        setStatusMessage("Заливаем...", false); // Показываем статус загрузки

        try {
            const response = await fetch('/api/posts/', {
                method: 'POST',
                body: formData, // FormData сама установит правильный Content-Type (multipart/form-data)
                // Не нужно устанавливать 'Content-Type' вручную при использовании FormData с файлами
            });

            if (response.ok) {
                setStatusMessage("Успешно!", false);
                postForm.reset(); // Очищаем форму
                // Опционально: обновить ленту или перенаправить пользователя
                // window.location.reload(); // Самый простой способ обновить
                // Или лучше перенаправить на профиль создавшего юзера
                 setTimeout(() => { // Небольшая задержка перед редиректом
                    window.location.href = `/profile/${encodeURIComponent(username)}`;
                 }, 1000);
            } else {
                const errorData = await response.json();
                console.error("Ошибка:", errorData);
                setStatusMessage(`Error: ${errorData.detail || response.statusText}`, true);
            }
        } catch (error) {
            console.error("Network error or other issue:", error);
            setStatusMessage("An error occurred while posting.", true);
        }
    });
}

function setStatusMessage(message, isError = false) {
    if (postStatus) {
        postStatus.textContent = message;
        postStatus.className = 'status-message'; // Сброс классов
        if (message) {
             postStatus.classList.add(isError ? 'error' : 'success');
        }
         // Очистка сообщения через некоторое время
         if (!isError && message.includes("success")) {
             setTimeout(() => {
                 postStatus.textContent = '';
                 postStatus.className = 'status-message';
             }, 3000); // Очистить через 3 секунды после успеха
         }
    }
}

// Можно добавить еще JS для динамической подгрузки постов при скролле (infinite scroll)
// или для лайков/комментариев, если расширять функционал.