document.addEventListener("DOMContentLoaded", function () {
      var coll = document.querySelectorAll(".collapsible");

      coll.forEach(function (button) {
        button.addEventListener("click", function () {
          this.classList.toggle("active");
          var content = this.nextElementSibling;
          content.classList.toggle("active");
        });
      });
    });