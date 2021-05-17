/*===== SHOW NAVBAR  =====*/
const showNavbar = (toggleId, navId, bodyId, headerId) => {
  const toggle = document.getElementById(toggleId),
    nav = document.getElementById(navId),
    bodypd = document.getElementById(bodyId),
    headerpd = document.getElementById(headerId);

  // Validate that all variables exist
  if (toggle && nav && bodypd && headerpd) {
    toggle.addEventListener("click", () => {
      // show navbar
      nav.classList.toggle("show");
      // change icon
      toggle.classList.toggle("bx-x");
      // add padding to body
      bodypd.classList.toggle("body-pd");
      // add padding to header
      headerpd.classList.toggle("body-pd");
    });
  }
};

showNavbar("header-toggle", "nav-bar", "body-pd", "header");

/*===== LINK ACTIVE  =====*/
const linkColor = document.querySelectorAll(".nav__link");

function colorLink() {
  if (linkColor) {
    linkColor.forEach((l) => l.classList.remove("activate"));
    this.classList.add("activate");
  }
}
linkColor.forEach((l) => l.addEventListener("click", colorLink));
anime.timeline({ loop: false }).add({
  targets: ".ml15 .word",
  scale: [14, 1],
  opacity: [0, 1],
  easing: "easeOutCirc",
  duration: 1000,
  delay: (el, i) => 800 * i,
});