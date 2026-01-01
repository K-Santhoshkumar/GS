document.addEventListener("DOMContentLoaded", () => {
  const bar = document.getElementById("progress-bar");
  if (!bar) return;

  const final = bar.style.getPropertyValue("--pct");
  bar.style.setProperty("--pct", "0%");
  setTimeout(() => bar.style.setProperty("--pct", final), 150);
});

// DELETE FILE
document.addEventListener("click", function (e) {
  if (!e.target.classList.contains("delete-file-btn")) return;

  const field = e.target.dataset.field;
  if (!confirm("Delete this file permanently?")) return;

  fetch(`?delete_file=1&field=${field}`, {
    method: "POST",
    headers: {
      "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
    },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.success) {
        e.target.closest(".uploaded").remove();
      } else {
        alert("Failed to delete file.");
      }
    });
});
// STEP 6 – Basic PAN auto-uppercase
document.addEventListener("DOMContentLoaded", () => {
  const addBtn = document.getElementById("add-signatory-btn");
  const container = document.getElementById("signatory-forms");
  const template = document.getElementById("signatory-template");

  if (!addBtn || !container || !template) return;

  addBtn.addEventListener("click", () => {
    if (container.children.length >= 4) {
      alert("Maximum 4 authorized signatories allowed.");
      return;
    }
    container.appendChild(template.content.cloneNode(true));
  });

  container.addEventListener("click", (e) => {
    if (e.target.classList.contains("remove-signatory")) {
      e.target.closest(".signatory-card").remove();
    }
  });
});
