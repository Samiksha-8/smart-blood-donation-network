/* =========================================
   ROLE SELECTION
========================================= */

const roleInputs =
    document.querySelectorAll('input[name="role"]');

const donorSection =
    document.getElementById("donorSection");

const bloodGroup =
    document.getElementById("bloodGroup");

const city =
    document.getElementById("city");

const dateOfBirth =
    document.getElementById("dateOfBirth");

const gender =
    document.getElementById("gender");

const weight =
    document.getElementById("weight");


function updateRoleFields() {

    const selectedRole =
        document.querySelector(
            'input[name="role"]:checked'
        ).value;


    if (selectedRole === "donor") {

        donorSection.style.display = "flex";

        bloodGroup.required = true;
        city.required = true;
        dateOfBirth.required = true;
        gender.required = true;
        weight.required = true;

    } else {

        donorSection.style.display = "none";

        bloodGroup.required = false;
        city.required = false;
        dateOfBirth.required = false;
        gender.required = false;
        weight.required = false;

    }
}


roleInputs.forEach(function (input) {

    input.addEventListener(
        "change",
        updateRoleFields
    );

});


updateRoleFields();

roleInputs.forEach(function (input) {

    input.addEventListener(
        "change",
        updateRoleFields
    );

});


updateRoleFields();



/* =========================================
   PASSWORD TOGGLE
========================================= */

const passwordToggles =
    document.querySelectorAll(".password-toggle");


passwordToggles.forEach(function (button) {

    button.addEventListener("click", function () {

        const targetId =
            button.getAttribute("data-target");

        const input =
            document.getElementById(targetId);


        const isPassword =
            input.type === "password";


        input.type =
            isPassword ? "text" : "password";


        button.textContent =
            isPassword ? "Hide" : "Show";

    });

});



/* =========================================
   FORM
========================================= */

const registerForm =
    document.getElementById("registerForm");


registerForm.addEventListener(
    "submit",
    function (event) {

        const password =
            document.getElementById(
                "registerPassword"
            ).value;

        const confirmPassword =
            document.getElementById(
                "confirmPassword"
            ).value;


        if (password !== confirmPassword) {

            event.preventDefault();

            alert("Passwords do not match.");

            return;
        }

        /*
            Passwords match.
            Allow the form to submit normally
            to the Flask backend.
        */

    }
);

// Preserve non-sensitive registration fields after a validation redirect.
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("registerForm");
    if (!form) return;

    const storageKey = "registrationFormData";
    const params = new URLSearchParams(window.location.search);

    // Restore previously entered fields, if available.
    try {
        const saved = sessionStorage.getItem(storageKey);

        if (saved) {
            const values = JSON.parse(saved);

            Object.entries(values).forEach(([name, value]) => {
                const fields = form.querySelectorAll(
                    `[name="${CSS.escape(name)}"]`
                );

                fields.forEach(field => {
                    if (field.type === "password") return;

                    if (field.type === "radio") {
                        field.checked = field.value === value;
                    } else if (field.type === "checkbox") {
                        field.checked = value === "true";
                    } else {
                        field.value = value;
                    }

                    field.dispatchEvent(new Event("change", {
                        bubbles: true
                    }));
                });
            });

            sessionStorage.removeItem(storageKey);
        }
    } catch (error) {
        sessionStorage.removeItem(storageKey);
    }

    // Save fields before submission, but never save passwords.
    form.addEventListener("submit", function () {
        const values = {};

        form.querySelectorAll("input, select, textarea").forEach(field => {
            if (!field.name || field.type === "password") return;

            if (field.type === "radio") {
                if (field.checked) values[field.name] = field.value;
            } else if (field.type === "checkbox") {
                values[field.name] = String(field.checked);
            } else {
                values[field.name] = field.value;
            }
        });

        sessionStorage.setItem(storageKey, JSON.stringify(values));
    });

    // Close the validation popup.
    const closeButton = document.getElementById("closeValidationModal");
    const modal = document.getElementById("validationModal");

    if (closeButton && modal) {
        closeButton.addEventListener("click", function () {
            modal.remove();
        });
    }
});