// Функция для установки фона на основе значения из localStorage
function setBackground() {
    var body = document.body;
    var currentBackground = localStorage.getItem("background");

    if (currentBackground === "dark") {
        body.style.backgroundImage = "url('/static/img/back_dark.png')";
    } else {
        body.style.backgroundImage = "url('/static/img/back_light.png')";
    }
}

// Установить фон при загрузке страницы
setBackground();
