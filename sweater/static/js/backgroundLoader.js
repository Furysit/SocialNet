
// Функция для установки фона на основе значения из localStorage
function setBackground() {
    var body = document.body;
    var currentBackground = localStorage.getItem("background");

    if (currentBackground === "dark") {
        body.style.backgroundImage = "url('/static/img/back_dark.png')";
        document.body.style.color = "white";
        let buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            button.style.color = "white"; // Меняем цвет текста на белый
        });
        let titles = document.querySelectorAll('b');
        titles.forEach(b => {
            b.style.color = "red";
        });
    } else {
        body.style.backgroundImage = "url('/static/img/back_light.png')";
        document.body.style.color = "";
    }
}

// Установить фон при загрузке страницы
setBackground();
