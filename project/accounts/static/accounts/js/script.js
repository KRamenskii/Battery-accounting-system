document.addEventListener('DOMContentLoaded', function() {
    const errorReportForm = document.getElementById('errorReportForm');
    const submitBtn = document.getElementById('submitBtn');
    const spinner = submitBtn?.querySelector('.spinner-border');
    const messagesContainer = document.getElementById('formMessages');
    
    // Проверка существования элементов
    if (!errorReportForm || !submitBtn || !spinner || !messagesContainer) {
        console.error('Required elements not found');
        return;
    }

    errorReportForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Показываем спиннер
        spinner.classList.remove('d-none');
        submitBtn.disabled = true;
        clearMessages();
        
        try {
            const formData = new FormData(this);
            
            const response = await fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                await handleSuccess(data);
            } else {
                handleValidationErrors(data);
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage(
                error.name === 'TypeError' 
                    ? 'Проверьте подключение к интернету' 
                    : 'Произошла ошибка при отправке формы', 
                'danger'
            );
        } finally {
            spinner.classList.add('d-none');
            submitBtn.disabled = false;
        }
    });
    
    function showMessage(text, type) {
        const alert = document.createElement('div');
        alert.className = `alert alert-${type} alert-dismissible fade show`;
        alert.innerHTML = `
            ${text}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        messagesContainer.appendChild(alert);
    }
    
    function clearMessages() {
        messagesContainer.innerHTML = '';
        document.querySelectorAll('.text-danger, .is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
            if (el.classList.contains('text-danger')) {
                el.remove();
            }
        });
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

    function handleSuccess(data) {
        showMessage(data.message, 'success');
        return new Promise(resolve => {
            setTimeout(() => {
                const modal = bootstrap.Modal.getInstance(document.getElementById('errorReportModal'));
                if (modal) modal.hide();
                errorReportForm.reset();
                clearMessages();
                resolve();
            }, 1500);
        });
    }

    function handleValidationErrors(data) {
        showMessage('Пожалуйста, исправьте ошибки в форме', 'danger');
        if (data.errors) {
            displayFormErrors(data.errors);
        }
    }
    
    // Очистка формы при закрытии модального окна
    const modalElement = document.getElementById('errorReportModal');
    if (modalElement) {
        modalElement.addEventListener('hidden.bs.modal', function () {
            errorReportForm.reset();
            clearMessages();
        });
    }
});

// Улучшенная версия dropdown
function toggleDropdown(button) {
    const dropdown = button.nextElementSibling;
    const isVisible = dropdown.classList.contains('show');
    
    // Закрываем все dropdown
    document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
        if (menu !== dropdown) {
            menu.classList.remove('show');
        }
    });
    
    // Переключаем текущий
    if (!isVisible) {
        dropdown.classList.add('show');
    }
}

// Делегирование событий для динамического контента
document.addEventListener('click', function(event) {
    const actionsContainer = event.target.closest('.actions-container');
    if (!actionsContainer) {
        document.querySelectorAll('.dropdown-menu.show').forEach(dropdown => {
            dropdown.classList.remove('show');
        });
    }
});

// Безопасное удаление
async function deleteError(url, csrfToken) {
    if (!confirm('Вы уверены, что хотите удалить эту ошибку?')) return;

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
            },
        });

        const data = await response.json();

        if (data.success) {
            // Можно добавить анимацию вместо перезагрузки
            location.reload();
        } else {
            alert(data.message || 'Ошибка при удалении');
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert('Ошибка сети при удалении');
    }
}

function editError(errorId) {
    // Логика редактирования
    window.location.href = `/edit-error/${errorId}/`;
}