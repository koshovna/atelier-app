const API_URL = 'http://localhost:5000/api';
const deleteClientModal = document.getElementById('deleteClientModal');
const closeDeleteBtn = document.querySelector('.close-delete');
const deleteClientForm = document.getElementById('deleteClientForm');
const deleteClientSurnameInput = document.getElementById('deleteClientSurname');
const cancelDeleteClientBtn = document.getElementById('cancelDeleteClientBtn');

let currentOrders = [];
let selectedOrderId = null;

// Навигация
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        
        const page = link.dataset.page;
        document.getElementById(`${page}Page`).classList.add('active');
        
        if (page === 'orders') loadOrders();
        if (page === 'clients') loadClients();
        if (page === 'analytics') showAnalytics();

    });
});

// Выход
document.getElementById('logoutBtn').addEventListener('click', () => {
    window.electronAPI.closeWindow();
});

// ЗАКАЗЫ
async function loadOrders(sortBy = '') {
    try {
        const url = sortBy ? `${API_URL}/orders?sort_by=${sortBy}` : `${API_URL}/orders`;
        const response = await fetch(url);
        currentOrders = await response.json();
        
        const tbody = document.getElementById('ordersTableBody');
        tbody.innerHTML = '';
        
        currentOrders.forEach((order, index) => {
            const row = tbody.insertRow();
            row.dataset.id = order.id;
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${order.client_surname}</td>
                <td>${order.order_number.slice(0, 8)}</td>
                <td>${order.product_name}</td>
                <td>${order.order_date}</td>
                <td>${order.completion_date}</td>
                <td>${order.master_surname}</td>
                <td>${order.cost} ₽</td>
            `;
            row.addEventListener('click', () => selectOrder(order.id, row));
        });

    } catch (error) {
        alert('Ошибка загрузки заказов: ' + error.message);
    }
}

function selectOrder(orderId, row) {
    document.querySelectorAll('#ordersTableBody tr').forEach(r => r.classList.remove('selected'));
    row.classList.add('selected');
    selectedOrderId = orderId;
    
    document.getElementById('editOrderBtn').disabled = false;
    document.getElementById('deleteOrderBtn').disabled = false;

    document.getElementById('editOrderBtn').classList.remove('btn-secondary');
    document.getElementById('editOrderBtn').classList.add('btn-primary');
}

function resetOrderButtons() {
    document.getElementById('editOrderBtn').disabled = true;
    document.getElementById('deleteOrderBtn').disabled = true;
    document.getElementById('editOrderBtn').classList.remove('btn-primary');
    document.getElementById('editOrderBtn').classList.add('btn-secondary');
}

resetOrderButtons();

function generateOrderNumber() {
    // Находим максимальный номер заказа
    const allNumbers = currentOrders.map(order => {
        const match = order.order_number.match(/ORD(\d+)/);
        return match ? parseInt(match[1], 10) : 0;
    });
    const maxNum = allNumbers.length ? Math.max(...allNumbers) : 0;
    // Создаём следующий номер
    const nextNum = (maxNum + 1).toString().padStart(3, '0');
    return `ORD${nextNum}`;
}

document.getElementById('sortSelect').addEventListener('change', (e) => {
    loadOrders(e.target.value);
});

// Модальное окно
const modal = document.getElementById('orderModal');
const closeBtn = document.querySelector('.close');
const cancelBtn = document.getElementById('cancelBtn');

document.getElementById('addOrderBtn').addEventListener('click', () => {
    document.getElementById('modalTitle').textContent = 'Добавить заказ';
    document.getElementById('orderForm').reset();
    selectedOrderId = null;
    document.getElementById('orderNumber').value = ""; // Поле пустое, UUID придёт с сервера
    document.getElementById('orderNumber').readOnly = true;
    modal.style.display = 'block';
});

document.getElementById('editOrderBtn').addEventListener('click', () => {
    if (!selectedOrderId) return;
    
    const order = currentOrders.find(o => o.id === selectedOrderId);
    if (!order) return;
    
    document.getElementById('modalTitle').textContent = 'Редактировать заказ';
    document.getElementById('clientSurname').value = order.client_surname;
    document.getElementById('orderNumber').value = order.order_number;
    document.getElementById('productName').value = order.product_name;
    document.getElementById('orderDate').value = order.order_date;
    document.getElementById('completionDate').value = order.completion_date;
    document.getElementById('masterSurname').value = order.master_surname;
    document.getElementById('cost').value = order.cost;
    
    modal.style.display = 'block';
});

closeBtn.onclick = () => modal.style.display = 'none';
cancelBtn.onclick = () => modal.style.display = 'none';

window.onclick = (event) => {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
};

document.getElementById('orderForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const orderData = {
        client_surname: document.getElementById('clientSurname').value,
        order_number: document.getElementById('orderNumber').value,
        product_name: document.getElementById('productName').value,
        order_date: document.getElementById('orderDate').value,
        completion_date: document.getElementById('completionDate').value,
        master_surname: document.getElementById('masterSurname').value,
        cost: parseFloat(document.getElementById('cost').value)
    };
    
    try {
        let response;
        if (selectedOrderId) {
            response = await fetch(`${API_URL}/orders/${selectedOrderId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderData)
            });
        } else {
            response = await fetch(`${API_URL}/orders`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(orderData)
            });
        }
        
        const result = await response.json();
        
        if (result.success) {
            modal.style.display = 'none';
            loadOrders();
            selectedOrderId = null;
            document.getElementById('editOrderBtn').disabled = true;
            document.getElementById('deleteOrderBtn').disabled = true;
        } else {
            alert('Ошибка: ' + result.message);
        }
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
});

document.getElementById('deleteOrderBtn').addEventListener('click', async () => {
    if (!selectedOrderId) return;
    
    if (!confirm('Вы уверены, что хотите удалить этот заказ?')) return;
    
    try {
        const response = await fetch(`${API_URL}/orders/${selectedOrderId}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        
        if (result.success) {
            loadOrders();
            selectedOrderId = null;
            document.getElementById('editOrderBtn').disabled = true;
            document.getElementById('deleteOrderBtn').disabled = true;
        }
    } catch (error) {
        alert('Ошибка удаления: ' + error.message);
    }
});

// Открытие модального окна для удаления по фамилии клиента
document.getElementById('deleteByClientBtn').addEventListener('click', () => {
    deleteClientSurnameInput.value = '';
    deleteClientModal.style.display = 'block';
});

// Закрытие модального окна
closeDeleteBtn.onclick = () => deleteClientModal.style.display = 'none';
cancelDeleteClientBtn.onclick = () => deleteClientModal.style.display = 'none';
window.onclick = (event) => {
    if (event.target == deleteClientModal) {
        deleteClientModal.style.display = 'none';
    }
}

// Обработка удаления клиента
deleteClientForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const surname = deleteClientSurnameInput.value.trim();
    if (!surname) return;

    if (!confirm(`Удалить все заказы клиента ${surname}?`)) return;

    try {
        const response = await fetch(`${API_URL}/orders/delete-by-client?surname=${surname}`, {
            method: 'DELETE'
        });

        const result = await response.json();
        alert(result.message);
        loadOrders();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
    deleteClientModal.style.display = 'none';
});


// КЛИЕНТЫ
async function loadClients(sortBy = 'client_surname') {
    try {
        const response = await fetch(`${API_URL}/clients?sort_by=${sortBy}`);
        const clients = await response.json();
        
        const tbody = document.getElementById('clientsTableBody');
        tbody.innerHTML = '';
        
        clients.forEach(client => {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${client.client_surname}</td>
                <td>${client.order_number}</td>
                <td>${client.duration}</td>
            `;
        });
    } catch (error) {
        alert('Ошибка загрузки клиентов: ' + error.message);
    }
}
function showAnalytics() {
    document.getElementById('masterResult').textContent = '';
    document.getElementById('maxCostResult').textContent = '';
    document.getElementById('avgCostResult').textContent = '';
    // Подгрузить реальные значения сразу!
    loadMaxCost();
    loadAvgCost();
}

async function loadMaxCost() {
    try {
        const response = await fetch(`${API_URL}/analytics/max-cost`);
        const result = await response.json();
        document.getElementById('maxCostResult').textContent =
            `Максимальная стоимость: ${result.max_cost} ₽`;
    } catch (error) {
        document.getElementById('maxCostResult').textContent = 'Ошибка!';
    }
}

async function loadAvgCost() {
    try {
        const response = await fetch(`${API_URL}/analytics/avg-cost`);
        const result = await response.json();
        document.getElementById('avgCostResult').textContent =
            `Средняя стоимость: ${result.avg_cost} ₽`;
    } catch (error) {
        document.getElementById('avgCostResult').textContent = 'Ошибка!';
    }
}

document.getElementById('clientSortSelect').addEventListener('change', (e) => {
    loadClients(e.target.value);
});

// АНАЛИТИКА
document.getElementById('searchMasterBtn').addEventListener('click', async () => {
    const master = document.getElementById('masterInput').value;
    if (!master) return;
    
    try {
        const response = await fetch(`${API_URL}/analytics/orders-by-master?master=${master}`);
        const result = await response.json();
        
        document.getElementById('masterResult').textContent = 
            `Заказов мастера ${master}: ${result.count}`;
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
});



// Загрузка заказов при запуске
loadOrders();
