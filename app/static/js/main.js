// Основные функции приложения

// Глобальная корзина
var cart = JSON.parse(localStorage.getItem('cart')) || [];

// Сохранение корзины в localStorage
function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
}

// Обновление счетчика корзины
function updateCartCount() {
    const count = cart.reduce((total, item) => total + item.quantity, 0);
    const cartCount = document.getElementById('cart-count');
    if (cartCount) {
        cartCount.textContent = count;
    }
}

// Добавление товара в корзину (глобальная функция)
function addToCart(productId) {
    console.log('Добавление в корзину товара ID:', productId);

    fetch(`/api/products/${productId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Товар не найден');
            }
            return response.json();
        })
        .then(product => {
            const existingItem = cart.find(item => item.id === product.id);

            if (existingItem) {
                if (existingItem.quantity >= product.stock_quantity) {
                    showNotification('Недостаточно товара на складе', 'error');
                    return;
                }
                existingItem.quantity++;
                console.log('Увеличено количество товара:', existingItem);
            } else {
                if (product.stock_quantity < 1) {
                    showNotification('Товара нет в наличии', 'error');
                    return;
                }
                cart.push({
                    id: product.id,
                    name: product.name,
                    price: product.price,
                    quantity: 1,
                    image: '/static/images/placeholder.jpg'
                });
                console.log('Добавлен новый товар:', product.name);
            }

            saveCart();
            showNotification('Товар добавлен в корзину');
        })
        .catch(error => {
            console.error('Ошибка добавления в корзину:', error);
            showNotification('Ошибка добавления товара', 'error');
        });
}

// Сделаем функцию глобальной
window.addToCart = addToCart;

// Показать уведомление
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem;
        background: ${type === 'success' ? '#28a745' : '#dc3545'};
        color: white;
        border-radius: 4px;
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Анимации для уведомлений
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Функция для отладки - просмотр содержимого корзины
function debugCart() {
    console.log('Содержимое корзины:', cart);
    console.log('LocalStorage cart:', localStorage.getItem('cart'));
    alert('Содержимое корзины выведено в консоль (F12)');
}

// Сделаем функцию глобальной
window.debugCart = debugCart;

// Обработка мобильного меню
document.addEventListener('DOMContentLoaded', function() {
    const menuBtn = document.querySelector('.mobile-menu-btn');
    const nav = document.querySelector('.nav');

    if (menuBtn && nav) {
        menuBtn.addEventListener('click', function() {
            nav.classList.toggle('show');
        });
    }

    // Закрытие меню при клике вне его
    document.addEventListener('click', function(e) {
        if (nav && nav.classList.contains('show') &&
            !e.target.closest('.nav') &&
            !e.target.closest('.mobile-menu-btn')) {
            nav.classList.remove('show');
        }
    });

    // Обновление счетчика корзины при загрузке
    updateCartCount();
});

// Базовая обработка ошибок fetch
async function handleFetch(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        showNotification('Ошибка соединения с сервером', 'error');
        throw error;
    }
}