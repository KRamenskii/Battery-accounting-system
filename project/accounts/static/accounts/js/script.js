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


document.addEventListener('DOMContentLoaded', function () {
    const editModalEl = document.getElementById('editErrorModal');
    if (!editModalEl) return; // если модалка не подключена — выходим

    const editModal = new bootstrap.Modal(editModalEl);
    const form = document.getElementById('editErrorForm');
    const messages = document.getElementById('editFormMessages');
    const saveBtn = document.getElementById('editSaveBtn');

    // Поля
    const inputId = document.getElementById('editErrorId');
    const selectType = document.getElementById('editErrorType');
    const textareaDesc = document.getElementById('editDescription');
    const selectStatus = document.getElementById('editStatus');
    const textareaFeedback = document.getElementById('editFeedback');

    // вспомогалки
    function clearMessages() {
        messages.innerHTML = '';
        document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    }
    function showMessage(text, type='danger') {
        const div = document.createElement('div');
        div.className = `alert alert-${type} alert-dismissible`;
        div.innerHTML = `${text} <button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
        messages.appendChild(div);
    }

    // Открыть модалку — запрос данных по id
    window.openEditModal = async function (errorId) {
        clearMessages();
        try {
            const resp = await fetch(`/accounts/api/error/${errorId}/`, {
                headers: {'X-Requested-With': 'XMLHttpRequest'}
            });
            if (!resp.ok) throw new Error('Ошибка при получении данных');
            const data = await resp.json();

            // Заполняем поля
            inputId.value = data.id;
            // error_type может быть null
            if (data.error_type) {
                selectType.value = data.error_type.id;
            } else {
                selectType.selectedIndex = 0;
            }
            textareaDesc.value = data.description ?? '';
            if (selectStatus) selectStatus.value = data.status ? data.status.id : '';
            if (textareaFeedback) textareaFeedback.value = data.feedback ?? '';

            // Права: сервер вернёт is_superuser
            const isAdmin = data.is_superuser === true;

            // Если админ: показать admin-only элементы и сделать type/desc readonly
            document.querySelectorAll('.admin-only').forEach(el => el.style.display = isAdmin ? '' : 'none');

            if (isAdmin) {
                // админ видит, но не редактирует тему/описание
                selectType.setAttribute('disabled', 'disabled');
                textareaDesc.setAttribute('disabled', 'disabled');
            } else {
                selectType.removeAttribute('disabled');
                textareaDesc.removeAttribute('disabled');
            }

            editModal.show();
        } catch (err) {
            console.error(err);
            showMessage('Не удалось загрузить данные обращения. Попробуйте ещё раз.', 'danger');
        }
    };

    // Обработка сабмита (AJAX POST)
    form.addEventListener('submit', async function (e) {
        e.preventDefault();
        clearMessages();

        saveBtn.disabled = true;
        saveBtn.textContent = 'Сохраняем...';

        const id = inputId.value;
        const url = `/accounts/api/error/${id}/update/`;

        const fd = new FormData();
        // Только поля, которые могут быть изменены:
        // Для пользователя: error_type, description
        // Для админа: status, feedback
        // Но отправим все — сервер сам проверит права.
        fd.append('error_type', selectType.value);
        fd.append('description', textareaDesc.value);
        if (selectStatus) fd.append('status', selectStatus.value);
        if (textareaFeedback) fd.append('feedback', textareaFeedback.value);

        // CSRF
        const csrf = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        try {
            const resp = await fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrf,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: fd
            });

            const data = await resp.json();
            if (!resp.ok) {
                // Приняли ошибки валидации
                if (data.errors) {
                    showMessage('Проверьте поля формы', 'danger');
                    for (const [field, msgs] of Object.entries(data.errors)) {
                        const el = document.querySelector(`[name="${field}"]`);
                        if (el) {
                            el.classList.add('is-invalid');
                        }
                    }
                } else {
                    showMessage(data.message || 'Ошибка при сохранении', 'danger');
                }
            } else {
                // Успех
                showMessage(data.message || 'Сохранено', 'success');
                // закрыть модалку и обновить список
                setTimeout(() => {
                    editModal.hide();
                    location.reload();
                }, 800);
            }
        } catch (err) {
            console.error(err);
            showMessage('Ошибка сети при сохранении', 'danger');
        } finally {
            saveBtn.disabled = false;
            saveBtn.textContent = 'Сохранить';
        }
    });

});