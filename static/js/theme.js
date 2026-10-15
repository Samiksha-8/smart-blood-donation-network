// ========================================
// THEME SYSTEM
// ========================================

function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);

    const themeIcon = document.getElementById("themeIcon");
    const themeText = document.getElementById("themeText");

    if (theme === "dark") {
        if (themeIcon) themeIcon.textContent = "☀";
        if (themeText) themeText.textContent = "Light";
    } else {
        if (themeIcon) themeIcon.textContent = "☾";
        if (themeText) themeText.textContent = "Dark";
    }
}


// ========================================
// TOGGLE THEME
// ========================================

function toggleTheme() {

    const currentTheme =
        document.documentElement.getAttribute("data-theme") || "light";

    const newTheme =
        currentTheme === "dark" ? "light" : "dark";

    localStorage.setItem("theme", newTheme);

    applyTheme(newTheme);
}


// ========================================
// LOAD SAVED THEME
// ========================================

document.addEventListener("DOMContentLoaded", function () {

    const savedTheme = localStorage.getItem("theme") || "light";

    applyTheme(savedTheme);

});