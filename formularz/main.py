import json

json_data = '''
{
  "formTitle": "Formularz Instalacji Implantu",
  "sections": [
    {
      "sectionTitle": "Dane Osobowe",
      "fields": [
        {
          "name": "name",
          "label": "Imię i Nazwisko",
          "type": "text",
          "placeholder": "Wprowadź imię i nazwisko",
          "required": true
        },
        {
          "name": "birthDate",
          "label": "Data Urodzenia",
          "type": "date",
          "required": true
        },
        {
          "name": "gender",
          "label": "Płeć",
          "type": "select",
          "options": ["mężczyzna", "kobieta", "inna"],
          "required": true
        },
        {
          "name": "idNumber",
          "label": "Numer ID",
          "type": "text",
          "placeholder": "Wprowadź numer ID",
          "required": true
        },
        {
          "name": "address",
          "label": "Adres",
          "type": "text",
          "placeholder": "Wprowadź adres",
          "required": true
        },
        {
          "name": "phoneEmail",
          "label": "Telefon i E-mail",
          "type": "textarea",
          "placeholder": "Wprowadź telefon i e-mail",
          "required": true
        }
      ]
    },
    {
      "sectionTitle": "Szczegóły Implantu",
      "fields": [
        {
          "name": "implantType",
          "label": "Typ Implantu",
          "type": "text",
          "placeholder": "Określ typ implantu",
          "required": true
        },
        {
          "name": "implantPurpose",
          "label": "Cel Implantu",
          "type": "textarea",
          "placeholder": "Wprowadź cel implantu"
        },
        {
          "name": "estheticPreferences",
          "label": "Preferencje Estetyczne",
          "type": "text",
          "placeholder": "Wprowadź preferencje estetyczne"
        },
        {
          "name": "installationDate",
          "label": "Preferowana Data Instalacji",
          "type": "date",
          "required": true
        },
        {
          "name": "preferredFacility",
          "label": "Preferowana Placówka",
          "type": "select",
          "options": ["gdańsk", "warszawa", "kraków"],
          "required": true
        }
      ]
    },
    {
      "sectionTitle": "Informacje Medyczne",
      "fields": [
        {
          "name": "bloodGroup",
          "label": "Grupa Krwi",
          "type": "select",
          "options": ["a", "b", "ab", "o"],
          "required": true
        },
        {
          "name": "rh",
          "label": "Czynnik RH",
          "type": "select",
          "options": ["pozytywny", "negatywny"],
          "required": true
        },
        {
          "name": "medicalHistory",
          "label": "Historia Medyczna",
          "type": "multi-select",
          "options": ["cukrzyca", "nadciśnienie", "alergie", "astma"]
        },
        {
          "name": "implantHistory",
          "label": "Poprzednie Implanty",
          "type": "multi-select",
          "options": ["implanty neuronalne", "bioniczne oko", "cyber-kończyna"]
        },
        {
          "name": "medications",
          "label": "Leki",
          "type": "textarea",
          "placeholder": "Wprowadź listę leków"
        }
      ]
    },
    {
      "sectionTitle": "Zgody",
      "fields": [
        {
          "name": "dataConsent",
          "label": "Zgoda na Przetwarzanie Danych",
          "type": "checkbox",
          "required": true
        },
        {
          "name": "installationConsent",
          "label": "Zgoda na Instalację Implantu",
          "type": "checkbox",
          "required": true
        },
        {
          "name": "marketingConsent",
          "label": "Zgoda na Marketing",
          "type": "checkbox"
        }
      ]
    },
    {
      "sectionTitle": "Dodatkowe Informacje",
      "fields": [
        {
          "name": "additionalRequirements",
          "label": "Dodatkowe Wymagania",
          "type": "textarea",
          "placeholder": "Wprowadź dodatkowe wymagania"
        }
      ]
    }
  ]
}
'''

def generate_html(js):
    form_html = f"""
    <head>
    <link rel="stylesheet" href="https://unpkg.com/sakura.css/css/sakura-dark.css" media="screen and (prefers-color-scheme: dark)" />
    </head>
    <img src="logo.png" alt="logo" style="width: 100px; height: 100px; display: block; margin-left: auto; margin-right: auto;">
    <form>\n<h1>{js['formTitle']}</h1>\n"""
    for section in js['sections']:
        form_html += f"  <fieldset>\n    <legend>{section['sectionTitle']}</legend>\n"
        
        for field in section['fields']:
            if field['type'] == 'text' or field['type'] == 'date':
                form_html += (
                    f"    <label for='{field['name']}'>{field['label']}</label>\n"
                    f"    <input type='{field['type']}' id='{field['name']}' name='{field['name']}' "
                    f"placeholder='{field.get('placeholder', '')}' "
                    f"{'required' if field.get('required') else ''} />\n"
                )
            elif field['type'] == 'textarea':
                form_html += (
                    f"    <label for='{field['name']}'>{field['label']}</label>\n"
                    f"    <textarea id='{field['name']}' name='{field['name']}' "
                    f"placeholder='{field.get('placeholder', '')}' "
                    f"{'required' if field.get('required') else ''}></textarea>\n"
                )
            elif field['type'] == 'select':
                form_html += (
                    f"    <label for='{field['name']}'>{field['label']}</label>\n"
                    f"    <select id='{field['name']}' name='{field['name']}' "
                    f"{'required' if field.get('required') else ''}>\n"
                )
                for option in field['options']:
                    form_html += f"      <option value='{option}'>{option}</option>\n"
                form_html += "    </select>\n"
            elif field['type'] == 'multi-select':
                form_html += (
                    f"    <label for='{field['name']}'>{field['label']}</label>\n"
                )
                for option in field['options']:
                    form_html += (
                        f"    <input type='checkbox' id='{option}' name='{field['name']}' "
                        f"value='{option}' /> <label for='{option}'>{option}</label><br/>\n"
                    )

            elif field['type'] == 'checkbox':
                form_html += (
                    f"    <input type='checkbox' id='{field['name']}' name='{field['name']}' "
                    f"{'required' if field.get('required') else ''} />\n"
                    f"    <label for='{field['name']}'>{field['label']}</label><br/>\n"
                )
                
        form_html += "  </fieldset>\n"
    
    form_html += "  <input type='submit' value='Zatwierdź' />\n</form>"
    return form_html

html_output = generate_html(json.loads(json_data))

with open("form.html", "w", encoding="utf-8") as f:
    f.write(html_output)
