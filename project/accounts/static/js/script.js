document.addEventListener('DOMContentLoaded', function() {
    const errorReportForm = document.getElementById('errorReportForm');
    const submitBtn = document.getElementById('submitBtn');
    const spinner = submitBtn.querySelector('.spinner-border');
    const messagesContainer = document.getElementById('formMessages');
    
    errorReportForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Показываем спиннер
        spinner.classList.remove('d-none');
        submitBtn.disabled = true;
        
        // Собираем данные формы
        const formData = new FormData(this);
        
        // Отправляем AJAX запрос
        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Успех - показываем сообщение и закрываем модальное окно
                showMessage(data.message, 'success');
                setTimeout(() => {
                    $('#errorReportModal').modal('hide');
                    errorReportForm.reset();
                    // Можно обновить страницу или таблицу с отчетами
                    // location.reload();
                }, 1500);
            } else {
                // Ошибки валидации
                showMessage('Пожалуйста, исправьте ошибки в форме', 'danger');
                displayFormErrors(data.errors);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Произошла ошибка при отправке формы', 'danger');
        })
        .finally(() => {
            // Скрываем спиннер
            spinner.classList.add('d-none');
            submitBtn.disabled = false;
        });
    });
    
    function showMessage(text, type) {
        messagesContainer.innerHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${text}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
    }
    
    function displayFormErrors(errors) {
        // Очищаем предыдущие ошибки
        document.querySelectorAll('.text-danger').forEach(el => el.remove());
        
        // Показываем новые ошибки
        for (const field in errors) {
            const input = document.querySelector(`[name="${field}"]`);
            if (input) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'text-danger small mt-1';
                errorDiv.textContent = errors[field][0];
                input.parentNode.appendChild(errorDiv);
            }
        }
    }
    
    // Очистка формы при закрытии модального окна
    $('#errorReportModal').on('hidden.bs.modal', function () {
        errorReportForm.reset();
        messagesContainer.innerHTML = '';
        document.querySelectorAll('.text-danger').forEach(el => el.remove());
    });
});