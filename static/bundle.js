$(document).ready(function(){
    $(".sidebar-toggle").on("click", function(t) {
        $(".app").toggleClass("is-collapsed");
        return false;
    });
    console.log('er');
});