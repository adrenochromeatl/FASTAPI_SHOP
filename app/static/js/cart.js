// Функции для работы с корзиной

// Загрузка корзины
function loadCart() {
    const emptyElement = document.getElementById('cart-empty');
    const contentElement = document.getElementById('cart-content');
    const itemsElement = document.getElementById('cart-items');

    if (cart.length === 0) {
        if (emptyElement) emptyElement.style.display = 'block';
        if (contentElement) contentElement.style.display = 'none';
        return;
    }

    if (emptyElement) emptyElement.style.display = 'none';
    if (contentElement) contentElement.style.display = 'grid';

    // Отображение товаров в корзине
    if (itemsElement) {
        itemsElement.innerHTML = cart.map(item => `
            <div class="cart-item">
                <img src="${item.image}" alt="${item.name}">
                <div class="cart-item-info">
                    <h4>${item.name}</h4>
                    <p class="price">${item.price} руб. × ${item.quantity}</p>
                    <p class="total">${item.price * item.quantity} руб.</p>
                </div>
                <div class="cart-item-actions">
                    <div class="quantity-control">
                        <button class="quantity-btn" onclick="updateQuantity(${item.id}, -1)">-</button>
                        <span>${item.quantity}</span>
                        <button class="quantity-btn" onclick="updateQuantity(${item.id}, 1)">+</button>
                    </div>
                    <button class="btn btn-outline" onclick="removeFromCart(${item.id})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `).join('');
    }

    updateCartSummary();
}

// Обновление количества товара
window.updateQuantity = function(productId, change) {
    const item = cart.find(item => item.id === productId);
    if (!item) return;

    // Проверка наличия на складе
    fetch(`/api/products/${productId}`)
        .then(response => response.json())
        .then(product => {
            const newQuantity = item.quantity + change;

            if (newQuantity < 1) {
                removeFromCart(productId);
                return;
            }

            if (newQuantity > product.stock_quantity) {
                showNotification('Недостаточно товара на складе', 'error');
                return;
            }

            item.quantity = newQuantity;
            saveCart();
            loadCart();
            showNotification('Корзина обновлена');
        })
        .catch(error => {
            console.error('Ошибка проверки наличия:', error);
            showNotification('Ошибка обновления корзины', 'error');
        });
};

// Удаление товара из корзины
window.removeFromCart = function(productId) {
    cart = cart.filter(item => item.id !== productId);
    saveCart();
    loadCart();
    showNotification('Товар удален из корзины');
};

// Обновление итоговой суммы
function updateCartSummary() {
    const totalItems = cart.reduce((total, item) => total + item.quantity, 0);
    const totalAmount = cart.reduce((total, item) => total + (item.price * item.quantity), 0);

    const totalItemsElement = document.getElementById('total-items');
    const totalAmountElement = document.getElementById('total-amount');

    if (totalItemsElement) totalItemsElement.textContent = totalItems;
    if (totalAmountElement) totalAmountElement.textContent = `${totalAmount} руб.`;
}

// Создание заказа
window.createOrder = function() {
    if (cart.length === 0) {
        showNotification('Корзина пуста', 'error');
        return;
    }

    const orderData = {
        products: cart.map(item => ({
            product_id: item.id,
            quantity: item.quantity
        }))
    };

    // В учебных целях используем фиксированный user_id
    fetch('/api/orders/?user_id=1', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw new Error(err.detail); });
        }
        return response.json();
    })
    .then(order => {
        // Очистка корзины после успешного заказа
        cart = [];
        saveCart();
        loadCart();

        showNotification('Заказ успешно создан!');

        // Перенаправление на страницу заказов
        setTimeout(() => {
            window.location.href = '/orders';
        }, 2000);
    })
    .catch(error => {
        console.error('Ошибка создания заказа:', error);
        showNotification(error.message || 'Ошибка создания заказа', 'error');
    });
};