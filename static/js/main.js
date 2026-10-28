const menuToggle = document.getElementById("menuToggle");
const mainNav = document.getElementById("mainNav");
if (menuToggle && mainNav) {
  menuToggle.addEventListener("click", () => mainNav.classList.toggle("open"));
  document.querySelectorAll("#mainNav a").forEach(link => link.addEventListener("click", () => mainNav.classList.remove("open")));
}
