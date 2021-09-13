/* IMPORTANT: be sure to correctly set which API url is in use */
const temp_api = "http://autotos.loca.lt/api/parse";
const real_api = "https://autotos.me/api/parse";
const mock_api = "http://localhost:3000/api/parse";
const digo_api = "https://68.183.26.237/api/parse";
const API_URL = digo_api;

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

// Given passage and excerpt strings, find the n characters surrounding
// the excerpt in the passage, on both sides.
// If the excerpt is not found, blanks are returned.
// If there are fewer than n characters, just give as much as we can.
function get_text_context(passage, excerpt, n) {
  const start = passage.indexOf(excerpt);
  if (start === -1) {
    return { before: "", after: "" };  // not found
  }

  const end = start + excerpt.length;
  const before = passage.slice(Math.max(start - n, 0), start);
  const after  = passage.slice(end, Math.min(end + n, passage.length));
  return { before: before, after: after };
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
    const verdict = document.getElementById("verdict");
    const predictions = content.predictions;
    const overall = content.sentiment;


    // sort statements by class
    // e.g. [{name: 'classname', examples: [...]}]
    let classes = [];
    predictions.forEach(prediction => {
      prediction.name = prediction.description;
      const matches = classes.filter(c => c.name === prediction.name);
      if (matches.length > 0) {
        matches[0].examples.push(prediction);
      } else {
        classes.push({
          name: prediction.name,
          examples: [prediction]
        });
      }
    });


    if (classes.length === 0) {
      show_elem("results-blank");
      hide_elem("results-table");
      verdict.textContent = "No Verdict";

    } else {
      hide_elem("results-blank");
      show_elem("results-table");

      if (overall < 4) {
        verdict.textContent = "Overall Verdict: Bad";
      } else if (overall <= 6) {
        verdict.textContent = "Overall Verdict: Neutral";
      } else {
        verdict.textContent = "Overall Verdict: Good";
      }

      verdict.textContent += " (" + overall + "/10)"

      const tbody = document.getElementsByTagName("tbody")[0];
      while (tbody.childNodes[0]) {
        tbody.removeChild(tbody.childNodes[0]);
      }

      classes.forEach(c => {
        const item = c.examples[0];
        const thumbs_icon = document.createElement("td");
        // const class_name  = document.createElement("td");
        const description = document.createElement("td");
        const source_text = document.createElement("td");

        const img = document.createElement("img");
        thumbs_icon.appendChild(img);
        if (item.effect === "good") {
          img.src = "img/thumbs-up.svg";
          thumbs_icon.classList.add("good");
        } else if (item.effect === "bad") {
          img.src = "img/thumbs-down.svg";
          thumbs_icon.classList.add("bad");
        } else {
          img.src = "img/meh-face.svg";
          thumbs_icon.classList.add("neutral");
        }

        // class_name.textContent = item.name;
        description.textContent = item.description;

        const row = document.createElement("tr");
        row.classList.add("regular");
        row.appendChild(thumbs_icon);
        // row.appendChild(class_name);
        row.appendChild(description);
        row.appendChild(source_text);
        tbody.appendChild(row);

        let open = false;
        const toggle = document.createElement("button");
        source_text.appendChild(toggle);
        const details = c.examples.map(item => {
          const details = document.createElement("tr");
          const text = document.createElement("td");
          const before = document.createElement("span");
          const source = document.createElement("span");
          const after  = document.createElement("span");
          const context = get_text_context(fulltext, item.text, 20);
          before.textContent = "..." + context.before;
          source.textContent = item.text;
          after.textContent  = context.after + "...";
          text.appendChild(before);
          text.appendChild(source);
          text.appendChild(after);
          text.colSpan = "4";
          text.classList.add("details");
          details.appendChild(text);
          source.classList.add("highlight");
          return details;
        });
        toggle.textContent = "more";
        toggle.addEventListener("click", _ => {
          if (!open) {
            toggle.textContent = "less";
            details.forEach(detail => {
              row.after(detail);
            });
            open = true;
          } else {
            toggle.textContent = "more";
            details.forEach(detail => {
              detail.parentNode.removeChild(detail);
            });
            open = false;
          }
        });
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
