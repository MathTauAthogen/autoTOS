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

function show_elem(id) {
  const elem = document.getElementById(id);
  elem.style.display = "block";
  return elem;
}

function hide_elem(id) {
  const elem = document.getElementById(id);
  elem.style.display = "none";
  return elem;
}

function parse(fulltext) {
  fetch("https://autotos.me/api/parse", {
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
      const table = show_elem("results-table");
      content.classes.forEach(item => {
        const thumbs_icon = document.createElement("td");
        const class_name  = document.createElement("td");
        const description = document.createElement("td");

        const img = document.createElement("img");
        thumbs_icon.appendChild(img);
        img.src = item.good ? "img/thumbs_up.svg" : "img/thumbs_down.svg";

        class_name.textContent = item.name;
        description.textContent = item.description;

        const row = document.createElement("tr");
        row.appendChild(thumbs_icon);
        row.appendChild(class_name);
        row.appendChild(description);
        table.appendChild(row);
      });
    }
    show_elem("results-container");

  }).catch(error => {
    // report error
    console.error(error);
    hide_elem("results-table");
    show_elem("error-box");
  });
}
