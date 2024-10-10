document.getElementById("changeBackgroundButton").addEventListener("click", function() {
    var currentBackground = localStorage.getItem("background");

    if (currentBackground === "dark") {
        localStorage.setItem("background", "light");
    } else {
        localStorage.setItem("background", "dark");
    }

    // Сразу применяем новый фон
    setBackground();
});

