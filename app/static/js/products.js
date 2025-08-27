// Функции для работы с товарами

// Добавление товара в корзину
function addToCart(productId) {
    fetch(`/api/products/${productId}`)
        .then(response => response.json())
        .then(product => {
            const existingItem = cart.find(item => item.id === product.id);

            if (existingItem) {
                if (existingItem.quantity >= product.stock_quantity) {
                    showNotification('Недостаточно товара на складе', 'error');
                    return;
                }
                existingItem.quantity++;
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
            }

            saveCart();
            showNotification('Товар добавлен в корзину');
        })
        .catch(error => {
            console.error('Ошибка добавления в корзину:', error);
            showNotification('Ошибка добавления товара', 'error');
        });
}

// Загрузка товаров по категории
function loadProductsByCategory(category) {
    let url = '/api/products?limit=100';
    if (category) {
        url += `&category=${encodeURIComponent(category)}`;
    }

    fetch(url)
        .then(response => response.json())
        .then(products => {
            displayProducts(products);
        })
        .catch(error => {
            console.error('Ошибка загрузки товаров:', error);
            showNotification('Ошибка загрузки товаров', 'error');
        });
}

// Поиск товаров
function searchProducts(query) {
    fetch('/api/products?limit=100')
        .then(response => response.json())
        .then(products => {
            const filtered = products.filter(product =>
                product.name.toLowerCase().includes(query.toLowerCase()) ||
                product.description.toLowerCase().includes(query.toLowerCase()) ||
                product.category.toLowerCase().includes(query.toLowerCase())
            );
            displayProducts(filtered);
        })
        .catch(error => {
            console.error('Ошибка поиска товаров:', error);
            showNotification('Ошибка поиска товаров', 'error');
        });
}

// Отображение товаров
function displayProducts(products) {
    const container = document.getElementById('products-container');
    if (!container) return;

    if (products.length === 0) {
        container.innerHTML = '<p class="no-products">Товары не найдены</p>';
        return;
    }

    container.innerHTML = products.map(product => `
        <div class="product-card">
            <img src="/static/images/placeholder.jpg" alt="${product.name}">
            <div class="product-info">
                <h3>${product.name}</h3>
                <p class="category">${product.category}</p>
                <p class="price">${product.price} руб.</p>
                <p class="stock">В наличии: ${product.stock_quantity} шт.</p>
                <button onclick="addToCart(${product.id})" class="btn btn-primary">
                    В корзину
                </button>
                <a href="/products/${product.id}" class="btn btn-outline">Подробнее</a>
            </div>
        </div>
    `).join('');
}