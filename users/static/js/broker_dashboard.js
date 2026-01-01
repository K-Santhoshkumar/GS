document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("menuToggle");
  const sidebar = document.getElementById("sidebar");
  const backdrop = document.getElementById("sidebarBackdrop");

  if (!btn) return;

  btn.addEventListener("click", () => {
    sidebar.classList.toggle("open");
    backdrop.classList.toggle("active");
    document.body.style.overflow =
      sidebar.classList.contains("open") ? "hidden" : "";
  });

  backdrop.addEventListener("click", () => {
    sidebar.classList.remove("open");
    backdrop.classList.remove("active");
    document.body.style.overflow = "";
  });
});
