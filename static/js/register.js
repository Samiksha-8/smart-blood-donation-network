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