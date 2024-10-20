function updateGenderText() {
    const genderSelect = document.getElementById('gender');
    const genderInfo = document.getElementById('gender-info');
    const selectedGender = genderSelect.value;

    if (selectedGender === 'male') {
        genderInfo.textContent = "W celu zapewnienia najwyższego poziomu bezpieczeństwa, potrzebujemy tych informacji, aby dostosować nasze usługi do Pana indywidualnych potrzeb i oczekiwań. Dziękujemy za zrozumienie.";
    } else if (selectedGender === 'female') {
        genderInfo.textContent = "W celu zapewnienia najwyższego poziomu bezpieczeństwa, potrzebujemy tych informacji, aby dostosować nasze usługi do Pani indywidualnych potrzeb i oczekiwań. Dziękujemy za zrozumienie.";
    } else {
        genderInfo.textContent = "W celu zapewnienia najwyższego poziomu bezpieczeństwa, potrzebujemy tych informacji, aby dostosować nasze usługi do Pana/Pani indywidualnych potrzeb i oczekiwań. Dziękujemy za zrozumienie.";
    }
}

// Funkcja do pokazania/ukrycia sekcji na podstawie zaznaczonych checkboxów
function toggleSection(checkboxes, sectionId) {
    const section = document.getElementById(sectionId);
    section.style.display = Array.from(checkboxes).some(ch => ch.checked) ? "block" : "none";
}

// Funkcja do pokazania/ukrycia opcji dodatkowych w zależności od rodzaju wszczepu
function updateAdditionalOptions() {
    const implantType = document.getElementById("implant-type").value;
    const additionalOptionsSelect = document.getElementById("additional-options");
    const additionalLabel = document.querySelector("label[for='additional-options']");

    if (implantType) {
        additionalLabel.style.display = "block"; // Pokazuje etykietę
        additionalOptionsSelect.style.display = "block"; // Pokazuje rozwijane menu
        
        // cyber-eye, cyber-arm, neural-implant
        // based on implant type, show different options
        switch (implantType) {
            case "cyber-eye":
                additionalOptionsSelect.innerHTML = `
                <select id="additional-options-select" name="additional-options">
                    <option value="night-vision">Night vision</option>
                    <option value="zoom">Zoom</option>
                    <option value="recording">Recording</option>
                </select>
                `;
                break;
            case "cyber-arm":
                additionalOptionsSelect.innerHTML = `
                <select id="additional-options-select" name="additional-options">
                    <option value="strength">Strength</option>
                    <option value="speed">Speed</option>
                    <option value="durability">Durability</option>
                </select>
                `;
                break;
            case "neural-implant":
                additionalOptionsSelect.innerHTML = `
                <select id="additional-options-select" name="additional-options">
                    <option value="memory">Memory</option>
                    <option value="processing">Processing</option>
                    <option value="interface">Interface</option>
                </select>
                `;
                break;
        }
        
    } else {
        additionalLabel.style.display = "none"; // Ukrywa etykietę
        additionalOptionsSelect.style.display = "none"; // Ukrywa rozwijane menu
    }
}

// Funkcja do ukrywania/wyświetlania opcji Rh
function toggleRhOptions() {
    const bloodGroup = document.getElementById("blood-group").value;
    const rhSelection = document.getElementById("rh-selection");

    rhSelection.style.display = (bloodGroup === "a" || bloodGroup === "b" || bloodGroup === "ab") ? "block" : "none"; // Pokazuje/ukrywa sekcję
}

// Dodaj zdarzenie dla wyboru grupy krwi
document.getElementById("blood-group").addEventListener("change", function() {
    toggleRhOptions();
    toggleRhOptions(); // Call to toggleRhOptions to update Rh options
});

// Dodaj zdarzenie dla wyboru rodzaju wszczepu
document.getElementById("implant-type").addEventListener("change", updateAdditionalOptions);

// Dodaj zdarzenia dla checkboxów chorób
const diseaseCheckboxes = document.querySelectorAll("input[name='disease']");
diseaseCheckboxes.forEach(checkbox => {
    checkbox.addEventListener("change", function() {
        toggleSection(diseaseCheckboxes, "risk-consent-section");
    });
});

// Dodaj zdarzenia dla checkboxów wszczepów
const implantCheckboxes = document.querySelectorAll("input[name='implant']");
implantCheckboxes.forEach(checkbox => {
    checkbox.addEventListener("change", function() {
        toggleSection(implantCheckboxes, "implants-risk-consent-section");
    });
});

// Dodaj zdarzenia dla checkboxów leków
const medicationCheckboxes = document.querySelectorAll("input[name='medication']");
medicationCheckboxes.forEach(checkbox => {
    checkbox.addEventListener("change", function() {
        toggleSection(medicationCheckboxes, "medications-risk-consent-section");
    });
});

// Function to validate form fields
function validateForm() {
    let isValid = true;

    // Get the required fields
    const implantType = document.getElementById('implant-type');
    const additionalOptionsSelect = document.getElementById('additional-options-select');

    // Clear previous error messages
    clearErrorMessages();

    // Validate implant type
    if (!implantType.value) {
        showError(implantType, "To pole jest wymagane.");
        isValid = false;
    }

    // Validate additional options if implant type is selected
    if (implantType.value && !additionalOptionsSelect.value) {
        showError(additionalOptionsSelect, "To pole jest wymagane.");
        isValid = false;
    }

    return isValid;
}

// Function to show error message
function showError(element, message) {
    const errorElement = document.createElement('span');
    errorElement.className = 'error-message';
    errorElement.style.color = 'red';
    errorElement.innerText = message;
    element.parentNode.appendChild(errorElement);
}

// Function to clear previous error messages
function clearErrorMessages() {
    const errorMessages = document.querySelectorAll('.error-message');
    errorMessages.forEach(function (errorMessage) {
        errorMessage.remove();
    });
}

// Example of form submission handler
document.getElementById('form').addEventListener('submit', function (event) {
    event.preventDefault();
    if (validateForm()) {
        // Submit the form
    }
});

// Domyślne ukrywanie sekcji
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("additional-options").style.display = "none";
    document.getElementById("rh-selection").style.display = "none";
    document.getElementById("risk-consent-section").style.display = "none";
    document.getElementById("implants-risk-consent-section").style.display = "none";
    document.getElementById("medications-risk-consent-section").style.display = "none";
});
