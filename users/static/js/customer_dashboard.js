document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.getElementById("sidebar");
  const openBtn = document.getElementById("menuToggle");
  const closeBtn = document.getElementById("closeSidebar");

  if (openBtn) {
    openBtn.addEventListener("click", function () {
      sidebar.classList.add("open");
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener("click", function () {
      sidebar.classList.remove("open");
    });
  }
});
