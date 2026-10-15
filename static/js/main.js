/* =========================================
   MOBILE MENU
========================================= */

const mobileMenu =
    document.getElementById("mobileMenu");

const sidebar =
    document.getElementById("sidebar");


if (mobileMenu) {

    mobileMenu.addEventListener("click", function () {

        sidebar.classList.toggle("open");

    });

}


/* =========================================
   AVAILABILITY TOGGLE
========================================= */

const availabilityToggle =
    document.getElementById("availabilityToggle");


if (availabilityToggle) {

    availabilityToggle.addEventListener(
        "change",
        function () {

            const status =
                document.querySelector(
                    ".availability-status strong"
                );

            const description =
                document.querySelector(
                    ".availability-box p"
                );

            const dot =
                document.querySelector(
                    ".online-dot"
                );


            if (availabilityToggle.checked) {

                if (status) {
                    status.textContent =
                        "Available to donate";
                }

                if (description) {
                    description.textContent =
                        "Your profile can currently appear in eligible donor searches.";
                }

                if (dot) {
                    dot.style.background =
                        "#16A34A";
                }

            } else {

                if (status) {
                    status.textContent =
                        "Not available";
                }

                if (description) {
                    description.textContent =
                        "Your profile will not be shown as available to recipients.";
                }

                if (dot) {
                    dot.style.background =
                        "#94A3B8";
                }

            }

        }
    );

}


/* =========================================
   LIGHT / DARK THEME
========================================= */

function applyTheme(theme) {

    document.documentElement.setAttribute(
        "data-theme",
        theme
    );

    const icon =
        document.getElementById("themeIcon");

    const text =
        document.getElementById("themeText");


    if (theme === "dark") {

        if (icon) {
            icon.textContent = "☀";
        }

        if (text) {
            text.textContent = "Light";
        }

    } else {

        if (icon) {
            icon.textContent = "☾";
        }

        if (text) {
            text.textContent = "Dark";
        }

    }

}


/* =========================================
   LOAD SAVED THEME
========================================= */

const savedTheme =
    localStorage.getItem("theme") || "light";

applyTheme(savedTheme);


/* =========================================
   THEME TOGGLE
========================================= */

function toggleTheme() {

    const currentTheme =
        document.documentElement.getAttribute(
            "data-theme"
        );

    const newTheme =
        currentTheme === "dark"
            ? "light"
            : "dark";


    localStorage.setItem(
        "theme",
        newTheme
    );

    applyTheme(newTheme);

}