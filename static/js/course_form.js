document.addEventListener("DOMContentLoaded", function () {
    const subjectField = document.getElementById("course-subject");
    const trainerDropdown = document.getElementById("course-trainer");
    const dateField = document.getElementById("course-date");
    const trainerWarning = document.getElementById("trainer-warning");

    console.log("Trainer Dropdown Found:", trainerDropdown);
    console.log("Date Field Found:", dateField);
    console.log("Trainer Warning Found:", trainerWarning);

    if (!subjectField || !trainerDropdown || !dateField || !trainerWarning) {
        console.error("❌ One or more required elements not found. Check IDs in HTML.");
        return;
    }

    function updateTrainers() {
        const subjectId = subjectField.value;
        const selectedDate = dateField.value;

        if (!subjectId || !selectedDate) {
            trainerDropdown.innerHTML = "<option value=''>-- Select Trainer --</option>";
            return;
        }

        console.log(`Fetching trainers for Subject ID: ${subjectId} and Date: ${selectedDate}`);

        fetch(`/services/get_trainers_by_subject/?subject_id=${subjectId}&date=${selectedDate}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    console.error("❌ Error:", data.error);
                    return;
                }

                console.log("Trainers Data Received:", data.trainers);

                trainerDropdown.innerHTML = "<option value=''>-- Select Trainer --</option>";
                trainerWarning.textContent = "";

                if (data.trainers.length === 0) {
                    console.warn("⚠️ No trainers available.");
                    trainerDropdown.innerHTML = "<option value=''>No trainers available</option>";
                }

                data.trainers.forEach(trainer => {
                    let option = document.createElement("option");
                    option.value = trainer.id;
                    option.textContent = `${trainer.name} - ${trainer.match_percentage}% match ${trainer.available ? "(🟢 Available)" : "(🔴 Booked)"}`;

                    if (!trainer.available) {
                        option.classList.add("trainer-booked");
                    } else if (trainer.match_percentage < 50) {
                        option.classList.add("trainer-not-recommended");
                    } else {
                        option.classList.add("trainer-available");
                    }

                    trainerDropdown.appendChild(option);
                });

                trainerDropdown.addEventListener("change", function () {
                    const selectedOption = trainerDropdown.options[trainerDropdown.selectedIndex];
                    if (selectedOption.classList.contains("trainer-not-recommended")) {
                        trainerWarning.textContent = "⚠️ Warning: This trainer has a low match percentage!";
                    } else {
                        trainerWarning.textContent = "";
                    }
                });
            })
            .catch(error => console.error("❌ Fetch Error:", error));
    }

    subjectField.addEventListener("change", updateTrainers);
    dateField.addEventListener("change", updateTrainers);
});
