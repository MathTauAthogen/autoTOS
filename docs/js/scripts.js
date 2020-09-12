/* here is what I envision the request will look like:
 *
 * {
 *   "text": "Lorem ipsum dolor sit amet..."
 * }
 *
 * and this is the response:
 *
 * {
 *   "classes": [
 *     {
 *       "name": "class 1 name",
 *       "description": "description of class 1",
 *       "good": true
 *     },
 *     {
 *       "name": "class 2 name",
 *       "description": "description of class 2",
 *       "good": false
 *     },
 *     ...
 *   ]
 * }
 */
const real_api = "https://autotos.me/api/parse";
const mock_api = "http://localhost:3000/api/parse";
const API_URL = mock_api;

function show_elem(id) {
  const elem = document.getElementById(id);
  elem.style.display = "block";
  return elem;
}

function hide_elem(id) {
  const elem = document.getElementById(id);
  elem.style.display = "none"
  return elem;
}

function run() {
  const text_entry = document.getElementsByTagName("textarea")[0];
  parse(text_entry.value);
}

function parse(fulltext) {
  fetch(API_URL, {
    method: "POST",
    headers: {
      "Accept": "application/json",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({text: fulltext})

  }).then(response => {
    return response.json();

  }).then(content => {
    if (content.classes.length === 0) {
      show_elem("results-blank");
      hide_elem("results-table");

    } else {
      hide_elem("results-blank");
      show_elem("results-table");

      const tbody = document.getElementsByTagName("tbody")[0];
      while (tbody.childNodes[0]) {
        tbody.removeChild(tbody.childNodes[0]);
      }

      content.classes.forEach(item => {
        const thumbs_icon = document.createElement("td");
        const class_name  = document.createElement("td");
        const description = document.createElement("td");

        const img = document.createElement("img");
        thumbs_icon.appendChild(img);
        if (item.good) {
          img.src = "img/thumbs-up.svg";
          thumbs_icon.classList.add("good");
        } else {
          img.src = "img/thumbs-down.svg";
          thumbs_icon.classList.add("bad");
        }

        class_name.textContent = item.name;
        description.textContent = item.description;

        const row = document.createElement("tr");
        row.appendChild(thumbs_icon);
        row.appendChild(class_name);
        row.appendChild(description);
        tbody.appendChild(row);
      });
    }
    const results = show_elem("results-container");
    results.style.display = "flex";

  }).catch(error => {
    // report error
    console.error(error);
    hide_elem("results-table");
    show_elem("error-box");
  });
}
