$(document).ready(function() {
  $(".sidebar-toggle").on("click", function(t) {
    $("body").toggleClass("is-collapsed");
    return false;
  });
  console.log("er");
});
