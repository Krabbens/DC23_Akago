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

// Form submission handler
document.getElementById('cyber-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = {
        name: document.getElementById('name').value,
        birthDate: document.getElementById('birth-date').value,
        gender: document.getElementById('gender').value,
        idNumber: document.getElementById('id-number').value,
        address: document.getElementById('address').value,
        phoneEmail: document.getElementById('phone-email').value,
        implantType: document.getElementById('implant-type').value,
        implantPurpose: document.getElementById('implant-purpose').value,
        estheticPreferences: document.getElementById('esthetic-preferences').value,
        installationDate: document.getElementById('installation-date').value,
        preferredFacility: document.getElementById('preferred-facility').value,
        additionalRequirements: document.getElementById('additional-requirements').value,
        bloodGroup: document.getElementById('blood-group').value,
        rh: document.getElementById('rh').value,
        medicalHistory: Array.from(document.querySelectorAll("input[name='disease']:checked")).map(el => el.value),
        implantHistory: Array.from(document.querySelectorAll("input[name='implant']:checked")).map(el => el.value),
        medications: Array.from(document.querySelectorAll("input[name='medication']:checked")).map(el => el.value),
        dataConsent: document.getElementById('data-consent').checked,
        installationConsent: document.getElementById('installation-consent').checked,
        marketingConsent: document.getElementById('marketing-consent') ? document.getElementById('marketing-consent').checked : false
    };

    const jsonData = JSON.stringify(formData, null, 2);
    console.log(jsonData);

    const xmlData = jsonToXml(formData);
    console.log(xmlData);
});

// Domyślne ukrywanie sekcji
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("additional-options").style.display = "none";
    document.getElementById("rh-selection").style.display = "none";
    document.getElementById("risk-consent-section").style.display = "none";
    document.getElementById("implants-risk-consent-section").style.display = "none";
    document.getElementById("medications-risk-consent-section").style.display = "none";
});


function jsonToXml(json, indent = "") {
    let xml = '';
    for (let key in json) {
        if (Array.isArray(json[key])) {
            xml += `${indent}<${key}>\n`;
            json[key].forEach(item => {
                xml += `${indent}  <item>${item}</item>\n`;
            });
            xml += `${indent}</${key}>\n`;
        } else if (typeof json[key] === "object" && json[key] !== null) {
            xml += `${indent}<${key}>\n`;
            xml += jsonToXml(json[key], indent + "  ");
            xml += `${indent}</${key}>\n`;
        } else {
            xml += `${indent}<${key}>${json[key]}</${key}>\n`;
        }
    }
    return xml;
}