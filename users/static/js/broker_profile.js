function setAction(action) {
  document.getElementById("action-field").value = action;
}

document.addEventListener("DOMContentLoaded", () => {
  const bar = document.getElementById("progress-bar");
  if (!bar) return;

  const finalWidth = bar.style.getPropertyValue("--pct");
  bar.style.setProperty("--pct", "0%");

  setTimeout(() => {
    bar.style.setProperty("--pct", finalWidth);
  }, 150);
});
document.addEventListener("click", function (e) {
  if (e.target.classList.contains("delete-file-btn")) {
    const field = e.target.getAttribute("data-field");

    if (!confirm("Delete this file permanently?")) return;

    fetch("?delete_file=1&field=" + field, {
      method: "POST",
      headers: {
        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]")
          .value,
      },
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.success) {
          e.target.parentElement.remove();
        } else {
          alert("Failed to delete file.");
        }
      });
  }
});
