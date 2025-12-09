function setAction(val) {
  document.getElementById("action-field").value = val;
}

document.addEventListener("DOMContentLoaded", () => {
  const bar = document.getElementById("progress-bar");
  if (!bar) return;

  const final = bar.style.getPropertyValue("--pct");
  bar.style.setProperty("--pct", "0%");
  setTimeout(() => bar.style.setProperty("--pct", final), 150);
});
