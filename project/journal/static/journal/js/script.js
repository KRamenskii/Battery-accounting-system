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

// Редактирование тестирований АБ и истории мест установок 
document.addEventListener('DOMContentLoaded', function () {
    // Глобальные переменные для хранения типа элемента
    let currentItemType = null;
    let currentItemId = null;
    
    // Обновляем функцию openEditModal
    function openEditModal() {
        if (!currentItemId || !currentItemType) {
            alert('Не удалось определить элемент для редактирования');
            hideContextMenu();
            return;
        }
        
        switch(currentItemType) {
            case 'test':
                // Определяем тип теста
                const testRow = document.querySelector(`.test-row[data-item-id="${currentItemId}"]`);
                if (testRow) {
                    const deleteUrl = testRow.getAttribute('data-delete-url');
                    if (deleteUrl.includes('dbt12d')) {
                        openTestDbt12dModal(currentItemId);
                    } else if (deleteUrl.includes('ic105')) {
                        openTestIc105Modal(currentItemId);
                    }
                }
                break;
            case 'installation':
                openInstallationModal(currentItemId);
                break;
            default:
                alert(`Редактирование элемента #${currentItemId}`);
        }
        
        hideContextMenu();
    }
    
    // Функция для открытия модалки DBT12D
    async function openTestDbt12dModal(testId) {
        try {
            const response = await fetch(`/journal/api/test/dbt12d/${testId}/`, {
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            });
            
            if (!response.ok) throw new Error('Ошибка при получении данных');
            const data = await response.json();
            
            // Заполняем форму
            document.getElementById('editTestDbt12dId').value = data.id;
            document.getElementById('editTestingDateDbt').value = data.testing_date;
            document.getElementById('editSOHDbt').value = data.SOH;
            document.getElementById('editSOCDbt').value = data.SOC;
            document.getElementById('editVOLDbt').value = data.VOL;
            document.getElementById('editRDbt').value = data.R;
            document.getElementById('editSTDDbt').value = data.STD;
            document.getElementById('editCCADbt').value = data.CCA;
            
            // Показываем модалку
            const modal = new bootstrap.Modal(document.getElementById('editTestDbt12dModal'));
            modal.show();
            
        } catch (error) {
            console.error(error);
            alert('Не удалось загрузить данные тестирования');
        }
    }
    
    // Функция для открытия модалки IC105
    async function openTestIc105Modal(testId) {
        try {
            const response = await fetch(`/journal/api/test/ic105/${testId}/`, {
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            });
            
            if (!response.ok) throw new Error('Ошибка при получении данных');
            const data = await response.json();
            
            document.getElementById('editTestIc105Id').value = data.id;
            document.getElementById('editTestingDateIc').value = data.testing_date;
            document.getElementById('editSOHIc').value = data.SOH;
            document.getElementById('editVOLIc').value = data.VOL;
            document.getElementById('editRIc').value = data.R;
            document.getElementById('editSTDIc').value = data.STD;
            document.getElementById('editCCAIc').value = data.CCA;
            
            const modal = new bootstrap.Modal(document.getElementById('editTestIc105Modal'));
            modal.show();
            
        } catch (error) {
            console.error(error);
            alert('Не удалось загрузить данные тестирования');
        }
    }
    
    // Функция для открытия модалки истории установки
    async function openInstallationModal(installationId) {
        try {
            const response = await fetch(`/journal/api/installation/${installationId}/`, {
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            });
            
            if (!response.ok) throw new Error('Ошибка при получении данных');
            const data = await response.json();
            
            document.getElementById('editInstallationId').value = data.id;
            document.getElementById('editInstallationLocation').value = data.installation_location_id;
            document.getElementById('editInstallationDate').value = data.installation_date;
            
            const modal = new bootstrap.Modal(document.getElementById('editInstallationModal'));
            modal.show();
            
        } catch (error) {
            console.error(error);
            alert('Не удалось загрузить данные истории установки');
        }
    }
    
    // Обработка формы DBT12D
    const editTestDbt12dForm = document.getElementById('editTestDbt12dForm');
    if (editTestDbt12dForm) {
        editTestDbt12dForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const testId = document.getElementById('editTestDbt12dId').value;
            const formData = new FormData(this);
            const messages = document.getElementById('editTestDbt12dMessages');
            
            try {
                const response = await fetch(`/journal/api/test/dbt12d/${testId}/update/`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(messages, data.message, 'success');
                    setTimeout(() => {
                        bootstrap.Modal.getInstance(document.getElementById('editTestDbt12dModal')).hide();
                        location.reload();
                    }, 1500);
                } else {
                    showMessage(messages, data.message || 'Ошибка при сохранении', 'danger');
                    if (data.errors) {
                        displayFormErrors(data.errors);
                    }
                }
            } catch (error) {
                console.error(error);
                showMessage(messages, 'Ошибка сети при сохранении', 'danger');
            }
        });
    }
    
    // Обработка формы IC105
    const editTestIc105Form = document.getElementById('editTestIc105Form');
    if (editTestIc105Form) {
        editTestIc105Form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const testId = document.getElementById('editTestIc105Id').value;
            const formData = new FormData(this);
            const messages = document.getElementById('editTestIc105Messages');
            
            try {
                const response = await fetch(`/journal/api/test/ic105/${testId}/update/`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(messages, data.message, 'success');
                    setTimeout(() => {
                        bootstrap.Modal.getInstance(document.getElementById('editTestIc105Modal')).hide();
                        location.reload();
                    }, 1500);
                } else {
                    showMessage(messages, data.message || 'Ошибка при сохранении', 'danger');
                    if (data.errors) {
                        displayFormErrors(data.errors);
                    }
                }
            } catch (error) {
                console.error(error);
                showMessage(messages, 'Ошибка сети при сохранении', 'danger');
            }
        });
    }
    
    // Обработка формы истории установки
    const editInstallationForm = document.getElementById('editInstallationForm');
    if (editInstallationForm) {
        editInstallationForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const installationId = document.getElementById('editInstallationId').value;
            const formData = new FormData(this);
            const messages = document.getElementById('editInstallationMessages');
            
            try {
                const response = await fetch(`/journal/api/installation/${installationId}/update/`, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage(messages, data.message, 'success');
                    setTimeout(() => {
                        bootstrap.Modal.getInstance(document.getElementById('editInstallationModal')).hide();
                        location.reload();
                    }, 1500);
                } else {
                    showMessage(messages, data.message || 'Ошибка при сохранении', 'danger');
                    if (data.errors) {
                        displayFormErrors(data.errors);
                    }
                }
            } catch (error) {
                console.error(error);
                showMessage(messages, 'Ошибка сети при сохранении', 'danger');
            }
        });
    }
    
    // Вспомогательные функции
    function showMessage(container, text, type = 'danger') {
        container.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show">
                ${text}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }
    
    function displayFormErrors(errors) {
        for (const [field, messages] of Object.entries(errors)) {
            const input = document.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.add('is-invalid');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'text-danger small mt-1';
                errorDiv.textContent = messages[0];
                input.parentNode.appendChild(errorDiv);
            }
        }
    }
    
    // Обновляем контекстное меню
    function initTableContextMenu() {
        const rows = document.querySelectorAll('.test-row');
        const contextDropdown = document.getElementById('contextDropdown');
        
        if (!contextDropdown) return;
        
        rows.forEach(row => {
            row.addEventListener('contextmenu', function(e) {
                e.preventDefault();
                
                selectedRowElement = this;
                selectedItemId = this.getAttribute('data-item-id');
                selectedItemType = this.getAttribute('data-item-type');
                selectedDeleteUrl = this.getAttribute('data-delete-url');
                
                // Сохраняем данные для глобального использования
                currentItemId = selectedItemId;
                currentItemType = selectedItemType;
                
                const x = e.pageX;
                const y = e.pageY;
                
                contextDropdown.style.left = x + 'px';
                contextDropdown.style.top = y + 'px';
                contextDropdown.style.display = 'block';
            });
        });
    }
    
    // Переопределяем глобальные функции
    window.openEditModal = openEditModal;
    window.deleteItem = deleteItem;
    
    // Инициализируем контекстное меню
    initTableContextMenu();
});