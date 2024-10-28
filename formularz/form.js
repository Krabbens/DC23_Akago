document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("implantForm").addEventListener("submit", function(event) {
      event.preventDefault();  // zapobiega domyślnej akcji przesyłania formularza
  
      const formData = new FormData(event.target);
      const dataObject = {};
  
      formData.forEach((value, key) => {
        if (dataObject[key]) {
          if (Array.isArray(dataObject[key])) {
            dataObject[key].push(value);
          } else {
            dataObject[key] = [dataObject[key], value];
          }
        } else {
          dataObject[key] = value;
        }
      });
  
      console.log(JSON.stringify(dataObject, null, 2));  // wyświetla dane w JSON
    });
  });
  