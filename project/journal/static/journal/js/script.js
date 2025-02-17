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