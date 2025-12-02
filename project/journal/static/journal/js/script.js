document.addEventListener("DOMContentLoaded", function () {
    const addButton = document.getElementById("addButton");
    const dropdownMenu = document.getElementById("dropdownMenu");

    addButton.addEventListener("click", function (event) {
        event.stopPropagation(); // Чтобы клик по кнопке не закрывал меню сразу
        dropdownMenu.classList.toggle("show");
    });

    // Закрытие меню при клике вне его
    document.addEventListener("click", function (event) {
        if (!dropdownMenu.contains(event.target) && event.target !== addButton) {
            dropdownMenu.classList.remove("show");
        }
    });
});

// Обработка нажатия на место установки
document.querySelectorAll('.installation-location-info').forEach(item => {
    item.addEventListener('click', () => {
        window.location.href = item.getAttribute('data-url');
    });
});

function toggleDropdown(event) {
    event.stopPropagation();
    const dropdown = document.getElementById('typeFilterDropdown');
    if (dropdown.style.display === 'block') {
        dropdown.style.display = 'none';
    } else {
        dropdown.style.display = 'block';
        // Прокрутка к активному элементу
        const activeItem = dropdown.querySelector('.active');
        if (activeItem) {
            activeItem.scrollIntoView({ block: 'nearest' });
        }
    }
}

document.addEventListener('click', function(event) {
    const dropdown = document.getElementById('typeFilterDropdown');
    if (!event.target.closest('.dropdown') && dropdown.style.display === 'block') {
        dropdown.style.display = 'none';
    }
});

// Запрещаем закрытие при клике внутри скроллящейся области
const scrollContainer = document.querySelector('.dropdown-scroll-container');
if (scrollContainer) { // Проверяем существование элемента
    scrollContainer.addEventListener('click', function(e) {
        e.stopPropagation();
    });
} else {
    console.log('Element .dropdown-scroll-container not found on this page');
}

// Обработка редактирования/удаления тестирований, истории мест установок
// Глобальные переменные для хранения данных выбранного элемента
let selectedItemId = null;
let selectedItemType = null;
let selectedRowElement = null;
let selectedDeleteUrl = null;
let selectedEditUrl = null;

// Функция инициализации контекстного меню
function initTableContextMenu() {
    const rows = document.querySelectorAll('.test-row');
    const contextDropdown = document.getElementById('contextDropdown');
    
    if (!contextDropdown) {
        console.log('Context dropdown not found on this page');
        return;
    }
    
    console.log('Found', rows.length, 'rows for context menu');
    
    rows.forEach(row => {
        // Обработка ПРАВОГО клика (contextmenu)
        row.addEventListener('contextmenu', function(e) {
            e.preventDefault();
    
            selectedRowElement = this;
            
            // Ищем ID в разных возможных атрибутах
            selectedItemId = this.getAttribute('data-item-id') || 
                            this.getAttribute('data-installation-id') || 
                            this.getAttribute('data-test-id');
            
            selectedItemType = this.getAttribute('data-item-type');
            selectedDeleteUrl = this.getAttribute('data-delete-url');
            
            console.log('Found data:', {
                id: selectedItemId,
                type: selectedItemType,
                url: selectedDeleteUrl,
                allIds: {
                    'data-item-id': this.getAttribute('data-item-id'),
                    'data-installation-id': this.getAttribute('data-installation-id'),
                    'data-test-id': this.getAttribute('data-test-id')
                }
            });
            
            // Позиционируем dropdown рядом с курсором
            const x = e.pageX;
            const y = e.pageY;
            
            contextDropdown.style.left = x + 'px';
            contextDropdown.style.top = y + 'px';
            contextDropdown.style.display = 'block';
        });
    });
    
    // Закрываем dropdown при клике в любом месте
    document.addEventListener('click', function(e) {
        if (contextDropdown && contextDropdown.style.display === 'block') {
            if (!contextDropdown.contains(e.target)) {
                hideContextMenu();
            }
        }
    });
    
    // Закрытие при нажатии ESC
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && contextDropdown && contextDropdown.style.display === 'block') {
            hideContextMenu();
        }
    });
    
    // Предотвращаем закрытие при клике на само меню
    contextDropdown.addEventListener('click', function(e) {
        e.stopPropagation();
    });
}

// УНИВЕРСАЛЬНАЯ ФУНКЦИЯ УДАЛЕНИЯ
function deleteItem() {    
    // Проверяем, есть ли данные
    if (!selectedItemId || !selectedItemType || !selectedDeleteUrl) {
        console.error('Missing required data for deletion');
        
        // Пробуем получить данные напрямую из элемента
        if (selectedRowElement) {
            console.log('Trying to get data directly from element:');
            selectedItemId = selectedRowElement.getAttribute('data-item-id');
            selectedItemType = selectedRowElement.getAttribute('data-item-type');
            selectedDeleteUrl = selectedRowElement.getAttribute('data-delete-url');
        }
        
        if (!selectedItemId || !selectedItemType || !selectedDeleteUrl) {
            alert('Ошибка: не удалось определить элемент для удаления');
            hideContextMenu();
            return;
        }
    }
    
    // Определяем сообщение подтверждения
    let confirmMessage = 'Вы уверены, что хотите удалить этот элемент?';
    
    if (!confirm(confirmMessage)) {
        hideContextMenu();
        return;
    }
    
    console.log('Sending DELETE request to:', selectedDeleteUrl);
    
    // AJAX запрос для удаления
    fetch(selectedDeleteUrl, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        if (response.ok) {
            // Удаляем строку из таблицы
            if (selectedRowElement) {
                selectedRowElement.remove();
                console.log('Row removed from table');
            }
            
            alert('Элемент успешно удален');
        } else {
            // Пробуем получить детали ошибки
            return response.json().then(data => {
                console.error('Error data:', data);
                throw new Error(data.error || 'Неизвестная ошибка');
            });
        }
    })
    .catch(error => {
        console.error('Fetch error:', error);
        alert('Ошибка при удалении: ' + error.message);
    })
    .finally(() => {
        hideContextMenu();
    });
}

// Функция редактирования (тоже универсальная)
function openEditModal() {
    console.log('=== EDIT ITEM ===');
    console.log('Item ID:', selectedItemId);
    console.log('Item Type:', selectedItemType);
    console.log('Edit URL:', selectedEditUrl);
    
    if (!selectedItemId || !selectedItemType) {
        alert('Не удалось определить элемент для редактирования');
        hideContextMenu();
        return;
    }
    
    if (selectedEditUrl) {
        // Если есть прямой URL для редактирования - переходим по нему
        window.location.href = selectedEditUrl;
    } else {
        // Или показываем сообщение
        alert(`Редактирование элемента #${selectedItemId}`);
    }
    
    hideContextMenu();
}

// Вспомогательная функция скрытия меню
function hideContextMenu() {
    const contextDropdown = document.getElementById('contextDropdown');
    if (contextDropdown) {
        contextDropdown.style.display = 'none';
    }
}

// Получение CSRF токена
function getCSRFToken() {
    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfTokenElement ? csrfTokenElement.value : '';
}

// Инициализация при загрузке DOM
document.addEventListener("DOMContentLoaded", function () {
    console.log('DOM loaded, initializing context menu...');
    initTableContextMenu();
});