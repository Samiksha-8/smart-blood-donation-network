const passwordInput =
    document.getElementById("password");

const passwordToggle =
    document.getElementById("passwordToggle");


passwordToggle.addEventListener(
    "click",
    function () {

        const isPassword =
            passwordInput.type === "password";


        passwordInput.type =
            isPassword ? "text" : "password";


        passwordToggle.textContent =
            isPassword ? "Hide" : "Show";


        passwordToggle.setAttribute(
            "aria-label",
            isPassword
                ? "Hide password"
                : "Show password"
        );

    }
);