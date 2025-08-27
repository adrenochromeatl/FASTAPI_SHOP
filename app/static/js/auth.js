// Функции для аутентификации

// Регистрация пользователя
function registerUser() {
    const form = document.getElementById('register-form');
    const formData = new FormData(form);

    const userData = {
        email: formData.get('email'),
        first_name: formData.get('first_name'),
        last_name: formData.get('last_name'),
        password: formData.get('password')
    };

    const confirmPassword = formData.get('confirm_password');

    // Валидация
    if (userData.password !== confirmPassword) {
        showNotification('Пароли не совпадают', 'error');
        return;
    }

    if (userData.password.length < 6) {
        showNotification('Пароль должен содержать минимум 6 символов', 'error');
        return;
    }

    fetch('/api/users/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.detail); });
        }
        return response.json();
    })
    .then(user => {
        showNotification('Регистрация успешна!');

        // Автоматический вход после регистрации
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
    })
    .catch(error => {
        console.error('Ошибка регистрации:', error);
        showNotification(error.message || 'Ошибка регистрации', 'error');
    });
}

// Вход пользователя
function loginUser() {
    const form = document.getElementById('login-form');
    const formData = new FormData(form);

    const loginData = {
        email: formData.get('email'),
        password: formData.get('password')
    };

    // В учебных целях используем простую проверку
    // В реальном приложении здесь был бы JWT токен
    if (loginData.email && loginData.password) {
        showNotification('Вход выполнен успешно!');

        // Сохранение информации о пользователе
        localStorage.setItem('currentUser', JSON.stringify({
            email: loginData.email
        }));

        setTimeout(() => {
            window.location.href = '/';
        }, 1000);
    } else {
        showNotification('Заполните все поля', 'error');
    }
}

// Проверка авторизации
function checkAuth() {
    const currentUser = JSON.parse(localStorage.getItem('currentUser'));
    const authLinks = document.querySelector('.auth-links');

    if (currentUser && authLinks) {
        authLinks.innerHTML = `
            <span class="nav-link">${currentUser.email}</span>
            <a href="#" class="nav-link" onclick="logout()">Выйти</a>
        `;
    }
}

// Выход
function logout() {
    localStorage.removeItem('currentUser');
    showNotification('Выход выполнен');
    setTimeout(() => {
        window.location.href = '/';
    }, 1000);
}

// Проверка авторизации при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
});