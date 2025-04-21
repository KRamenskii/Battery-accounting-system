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
document.querySelector('.dropdown-scroll-container').addEventListener('click', function(e) {
    e.stopPropagation();
});