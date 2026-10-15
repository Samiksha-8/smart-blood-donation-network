const mobileMenu =
    document.getElementById("mobileMenu");

const sidebar =
    document.getElementById("sidebar");


if (mobileMenu) {

    mobileMenu.addEventListener("click", function () {

        sidebar.classList.toggle("open");

    });

}

/* Availability toggle */

const availabilityToggle =
    document.getElementById("availabilityToggle");

if (availabilityToggle) {

    availabilityToggle.addEventListener("change", async function () {

        const status =
            document.querySelector(".availability-status strong");

        const description =
            document.querySelector(".availability-box p");

        const dot =
            document.querySelector(".online-dot");

        const isAvailable = availabilityToggle.checked;

        try {

            const response = await fetch("/donor/availability", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    is_available: isAvailable
                })
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.message);
            }

            if (isAvailable) {

                status.textContent = "Available to donate";

                description.textContent =
                    "Your profile can currently appear in eligible donor searches.";

                dot.style.background = "#16A34A";

            } else {

                status.textContent = "Not available";

                description.textContent =
                    "Your profile will not be shown as available to recipients.";

                dot.style.background = "#94A3B8";
            }

        } catch (error) {

            console.error("Availability update failed:", error);

            // Restore previous checkbox state
            availabilityToggle.checked = !isAvailable;

            alert("Could not update availability. Please try again.");
        }

    });

}