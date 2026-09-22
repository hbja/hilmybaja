document.addEventListener("DOMContentLoaded", function () {
  var coll = document.querySelectorAll(".collapsible");

  coll.forEach(function (button) {
    button.addEventListener("click", function () {
      var isOpen = this.getAttribute("aria-expanded") === "true";
      var content = this.nextElementSibling;

      this.classList.toggle("active", !isOpen);
      this.setAttribute("aria-expanded", String(!isOpen));
      content.classList.toggle("active", !isOpen);
      content.hidden = isOpen;
    });
  });
});
